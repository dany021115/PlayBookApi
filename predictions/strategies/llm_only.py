"""LLM-driven pick: ask the model to choose market+outcome+confidence given context.

If the LLM is unavailable / no API key, returns None (other strategies still run).
"""

from __future__ import annotations

import json
import logging
from decimal import Decimal

from predictions.strategies.base import BasePickStrategy, Pick

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "Eres analista deportivo experto. Recibes datos de un partido y mercados de apuestas. "
    "Devuelve EXCLUSIVAMENTE un JSON válido, sin texto adicional, con esta forma exacta:\n"
    "{\"market\": \"h2h\"|\"totals\"|\"spreads\", "
    "\"outcome\": \"home\"|\"away\"|\"draw\"|\"over\"|\"under\", "
    "\"line\": null|number, "
    "\"confidence\": 0-100, "
    "\"reasoning\": \"explicación breve en español de 2-3 frases\"}\n"
    "No uses lenguaje vago. Cita datos concretos del contexto. No inventes datos."
)


class LLMOnlyStrategy(BasePickStrategy):
    name = "llm_only"

    def run(self, event, features: dict) -> Pick | None:
        from django.conf import settings

        if not settings.LLM_API_KEY:
            return None
        try:
            from openai import OpenAI
        except ImportError:
            logger.warning("openai SDK not installed")
            return None

        try:
            client = OpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
            completion = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(event, features)},
                ],
                temperature=0.4,
                max_tokens=400,
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content
            data = json.loads(content)
        except Exception as exc:
            logger.warning("llm_only strategy failed: %s", exc)
            return None

        market = data.get("market")
        outcome = data.get("outcome")
        confidence = int(data.get("confidence") or 0)
        if not market or not outcome or confidence < int(self.params.get("min_confidence", 60)):
            return None

        # Find a real bookmaker price for the chosen pick from features
        market_data = (features.get("market_odds") or {}).get(market) or []
        line_val = data.get("line")
        for entry in market_data:
            if entry["outcome"] != outcome:
                continue
            if line_val is not None and float(entry.get("line") or 0) != float(line_val):
                continue
            if entry.get("snapshots"):
                best = max(entry["snapshots"], key=lambda s: float(s.get("price", 0)))
                pick = Pick(
                    market=market,
                    outcome=outcome,
                    line=Decimal(str(line_val)) if line_val is not None else None,
                    bookmaker_id=int(best["bookmaker_id"]),
                    price=Decimal(str(best["price"])),
                    confidence=min(95, max(0, confidence)),
                )
                # Stash the LLM-generated reasoning so feature_builder/task can pick it up
                features["__llm_reasoning"] = data.get("reasoning") or ""
                return pick
        return None


def _build_user_prompt(event, features: dict) -> str:
    home = event.home_team.name
    away = event.away_team.name
    league = event.league.name
    start = event.start_time.isoformat()
    form = features.get("form") or {}
    avg = features.get("avg_goals") or {}
    market_data = features.get("market_odds") or {}

    def _best_summary(market_key: str, outcome: str) -> str:
        for entry in market_data.get(market_key, []):
            if entry["outcome"] == outcome and entry.get("snapshots"):
                best = max(entry["snapshots"], key=lambda s: float(s.get("price", 0)))
                return f"{best['price']} ({best.get('bookmaker_slug', '?')})"
        return "-"

    return (
        f"Partido: {home} vs {away} | Liga: {league} | Hora: {start}\n"
        f"Forma últimos 5 ({home}): {''.join(form.get('home') or []) or '-'}\n"
        f"Forma últimos 5 ({away}): {''.join(form.get('away') or []) or '-'}\n"
        f"Promedio goles {home}: {avg.get('home', '-')} | {away}: {avg.get('away', '-')}\n"
        f"Mejores cuotas H2H: home={_best_summary('h2h','home')}, "
        f"draw={_best_summary('h2h','draw')}, away={_best_summary('h2h','away')}\n"
        f"Totals 2.5: over={_best_summary('totals','over')}, "
        f"under={_best_summary('totals','under')}\n"
        f"Decide la mejor apuesta y explica el porqué."
    )
