"""Celery tasks: generate + settle predictions."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from markets.models import Event
from predictions.models import FeatureVector, Prediction, Strategy
from predictions.services.feature_builder import build_features
from predictions.services.llm_explainer import explain
from predictions.strategies import STRATEGY_REGISTRY

logger = logging.getLogger(__name__)


@shared_task(name="predictions.tasks.generate_predictions", bind=True, max_retries=2)
def generate_predictions(self, hours_ahead: int = 48) -> dict[str, int]:
    now = timezone.now()
    upper = now + timedelta(hours=hours_ahead)
    lower = now + timedelta(minutes=15)
    events = (
        Event.objects.filter(
            status=Event.Status.SCHEDULED,
            start_time__gte=lower,
            start_time__lte=upper,
        )
        .select_related("league__sport", "home_team", "away_team")
    )
    strategies = list(Strategy.objects.filter(enabled=True))

    counts: dict[str, int] = {"events_seen": 0, "predictions_created": 0, "skipped": 0}

    for event in events:
        counts["events_seen"] += 1
        try:
            features = build_features(event)
        except Exception as exc:
            logger.warning("feature_builder failed for event %s: %s", event.id, exc)
            counts["skipped"] += 1
            continue

        fv = FeatureVector.objects.create(event=event, payload=features)

        for strat_row in strategies:
            cls = STRATEGY_REGISTRY.get(strat_row.type)
            if cls is None:
                continue
            try:
                pick = cls(strat_row.params or {}).run(event, features)
            except Exception as exc:
                logger.warning("strategy %s crashed on event %s: %s",
                               strat_row.name, event.id, exc)
                continue
            if pick is None:
                continue

            # Avoid duplicates: same (event, strategy, market, outcome)
            exists = Prediction.objects.filter(
                event=event, strategy=strat_row,
                market=pick.market, outcome=pick.outcome,
            ).exists()
            if exists:
                continue

            llm_reasoning = features.pop("__llm_reasoning", None)
            try:
                reasoning = llm_reasoning or explain(event, features, pick)
            except Exception as exc:
                logger.warning("explainer failed: %s", exc)
                reasoning = ""

            try:
                with transaction.atomic():
                    Prediction.objects.create(
                        event=event,
                        strategy=strat_row,
                        feature_vector=fv,
                        market=pick.market,
                        outcome=pick.outcome,
                        line=pick.line,
                        recommended_bookmaker_id=pick.bookmaker_id,
                        recommended_price=pick.price,
                        confidence=pick.confidence,
                        reasoning=reasoning,
                    )
                    counts["predictions_created"] += 1
            except Exception as exc:
                logger.warning(
                    "create Prediction failed (event=%s strat=%s market=%s outcome=%s): %s",
                    event.id, strat_row.name, pick.market, pick.outcome, exc,
                )
    logger.info("generate_predictions: %s", counts)
    return counts


@shared_task(name="predictions.tasks.settle_predictions", bind=True, max_retries=2)
def settle_predictions(self) -> dict[str, int]:
    """Settle predictions whose Event has finished but Prediction is still pending."""
    counts = {"settled": 0, "won": 0, "lost": 0, "push": 0, "void": 0}
    pending = (
        Prediction.objects.filter(status=Prediction.Status.PENDING)
        .select_related("event")
    )
    for pred in pending:
        ev = pred.event
        if ev.status not in (Event.Status.FINISHED, Event.Status.CANCELED, Event.Status.POSTPONED):
            continue
        if ev.status != Event.Status.FINISHED or ev.home_score is None or ev.away_score is None:
            pred.status = Prediction.Status.VOIDED
            pred.result = Prediction.Result.VOID
            pred.settled_at = timezone.now()
            pred.save(update_fields=["status", "result", "settled_at"])
            counts["void"] += 1
            continue
        result = _decide_result(pred, ev.home_score, ev.away_score)
        pred.result = result
        pred.status = Prediction.Status.SETTLED
        pred.settled_at = timezone.now()
        pred.save(update_fields=["status", "result", "settled_at"])
        counts["settled"] += 1
        counts[result] = counts.get(result, 0) + 1
    logger.info("settle_predictions: %s", counts)
    return counts


def _decide_result(pred: Prediction, home: int, away: int) -> str:
    market = pred.market
    outcome = pred.outcome
    line = float(pred.line) if pred.line is not None else 0.0
    total = home + away

    if market == "h2h":
        if outcome == "home":
            return "won" if home > away else "lost"
        if outcome == "away":
            return "won" if away > home else "lost"
        if outcome == "draw":
            return "won" if home == away else "lost"
    elif market == "totals":
        if outcome == "over":
            if total > line:
                return "won"
            if total == line:
                return "push"
            return "lost"
        if outcome == "under":
            if total < line:
                return "won"
            if total == line:
                return "push"
            return "lost"
    elif market == "spreads":
        if outcome == "home":
            adj = home + line
            if adj > away:
                return "won"
            if adj == away:
                return "push"
            return "lost"
        if outcome == "away":
            adj = away + line
            if adj > home:
                return "won"
            if adj == home:
                return "push"
            return "lost"
    return "void"
