"""Generate human-readable Spanish reasoning for a Pick using the LLM."""

from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "Eres analista deportivo experto. Genera explicaciones BREVES (2-3 frases) en ESPAÑOL "
    "para tips de apuesta. Cita datos concretos del contexto que recibes. "
    "NO uses lenguaje vago. NO inventes datos. NO uses emojis. NO añadas saludos ni disclaimers."
)


def explain(event, features: dict, pick) -> str:
    """Return reasoning string. Falls back to template if LLM unavailable."""
    if not settings.LLM_API_KEY:
        return _fallback(event, features, pick)
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )
        completion = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _user_prompt(event, features, pick)},
            ],
            temperature=0.4,
            max_tokens=200,
        )
        text = (completion.choices[0].message.content or "").strip()
        if text:
            return text
    except Exception as exc:
        logger.warning("llm_explainer failed: %s", exc)
    return _fallback(event, features, pick)


def _user_prompt(event, features: dict, pick) -> str:
    home = event.home_team.name
    away = event.away_team.name
    league = event.league.name
    form = features.get("form") or {}
    avg = features.get("avg_goals") or {}
    h2h = features.get("h2h") or []
    market_data = features.get("market_odds") or {}

    def _best(market: str, outcome: str) -> str:
        for entry in market_data.get(market, []):
            if entry["outcome"] == outcome and entry.get("snapshots"):
                best = max(entry["snapshots"], key=lambda s: float(s.get("price", 0)))
                return f"{best['price']} ({best.get('bookmaker_slug', '?')})"
        return "-"

    pick_line = f" line={pick.line}" if pick.line is not None else ""
    h2h_summary = " | ".join(f"{m['date']} {m['home']} {m['score']} {m['away']}" for m in h2h) or "-"

    return (
        f"Partido: {home} vs {away} | Liga: {league}\n"
        f"Forma últimos 5 ({home}): {''.join(form.get('home') or []) or '-'}\n"
        f"Forma últimos 5 ({away}): {''.join(form.get('away') or []) or '-'}\n"
        f"Promedio goles {home}: {avg.get('home', '-')} | {away}: {avg.get('away', '-')}\n"
        f"H2H últimos: {h2h_summary}\n"
        f"Mejores cuotas: H2H home={_best('h2h','home')}, draw={_best('h2h','draw')}, "
        f"away={_best('h2h','away')}; Totals over={_best('totals','over')}, "
        f"under={_best('totals','under')}\n"
        f"\nMi sistema sugiere apostar:\n"
        f"  Market: {pick.market} | Outcome: {pick.outcome}{pick_line}\n"
        f"  Cuota: {pick.price} | Confianza: {pick.confidence}/100\n"
        f"\nResponde SOLO con la explicación en 2-3 frases."
    )


def _fallback(event, features: dict, pick) -> str:
    """Template-based reasoning when LLM is unavailable."""
    home = event.home_team.name
    away = event.away_team.name
    form = features.get("form") or {}
    home_form = "".join(form.get("home") or []) or "-"
    away_form = "".join(form.get("away") or []) or "-"
    avg = features.get("avg_goals") or {}
    pick_line = f" {pick.line}" if pick.line is not None else ""
    return (
        f"Apuesta sugerida: {pick.market}/{pick.outcome}{pick_line} @ {pick.price}. "
        f"Forma reciente {home}={home_form}, {away}={away_form}. "
        f"Promedio goles {home}: {avg.get('home', '-')} | {away}: {avg.get('away', '-')}. "
        f"Confianza: {pick.confidence}/100."
    )
