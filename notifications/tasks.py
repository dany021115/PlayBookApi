"""Celery tasks for push notifications + fan-out."""

from __future__ import annotations

import logging
from typing import Any

from celery import shared_task

from notifications.models import DeviceToken, NotificationLog
from notifications.services.fcm import send_to_token

logger = logging.getLogger(__name__)


@shared_task(name="notifications.tasks.send_push", bind=True, max_retries=2,
             default_retry_delay=10)
def send_push(self, user_id: int, kind: str, title: str, body: str,
              data: dict[str, Any] | None = None) -> dict[str, int]:
    counts = {"sent": 0, "failed": 0}
    tokens = DeviceToken.objects.filter(user_id=user_id, active=True)
    for dt in tokens:
        ok, msg_id, err = send_to_token(dt.token, title, body, data)
        NotificationLog.objects.create(
            user_id=user_id, kind=kind, title=title, body=body,
            payload=data or {}, success=ok, error=err, fcm_message_id=msg_id,
        )
        if ok:
            counts["sent"] += 1
        else:
            counts["failed"] += 1
            if "INVALID_ARGUMENT" in err or "NOT_FOUND" in err or "Requested entity was not found" in err:
                dt.active = False
                dt.save(update_fields=["active"])
    return counts


@shared_task(name="follows.tasks.fan_out_new_prediction", bind=True, max_retries=1)
def fan_out_new_prediction(self, prediction_id: int) -> dict[str, int]:
    from follows.models import FollowedLeague, FollowedSport, FollowedStrategy
    from predictions.models import Prediction

    pred = (
        Prediction.objects
        .select_related("event__league__sport", "event__home_team", "event__away_team",
                        "strategy", "recommended_bookmaker")
        .filter(id=prediction_id)
        .first()
    )
    if pred is None:
        return {"recipients": 0}

    event = pred.event
    league = event.league
    sport = league.sport

    user_ids = set()
    user_ids.update(FollowedSport.objects.filter(sport=sport).values_list("user_id", flat=True))
    user_ids.update(FollowedLeague.objects.filter(league=league).values_list("user_id", flat=True))
    user_ids.update(FollowedStrategy.objects.filter(strategy=pred.strategy).values_list("user_id", flat=True))

    title = f"Nueva predicción: {event.home_team.name} vs {event.away_team.name}"
    body = (
        f"[{pred.strategy.name}] {pred.market}/{pred.outcome}"
        + (f" {pred.line}" if pred.line is not None else "")
        + f" @ {pred.recommended_price} ({pred.recommended_bookmaker.slug})"
    )
    data = {
        "kind": "new_prediction",
        "prediction_id": pred.id,
        "event_id": event.id,
        "sport": sport.key,
    }
    for uid in user_ids:
        send_push.delay(uid, "new_prediction", title, body, data)
    return {"recipients": len(user_ids)}


@shared_task(name="follows.tasks.fan_out_settled_prediction", bind=True, max_retries=1)
def fan_out_settled_prediction(self, prediction_id: int) -> dict[str, int]:
    """Notify users who SAVED this prediction once it settles."""
    from follows.models import SavedPrediction
    from predictions.models import Prediction

    pred = (
        Prediction.objects
        .select_related("event__home_team", "event__away_team")
        .filter(id=prediction_id)
        .first()
    )
    if pred is None:
        return {"recipients": 0}

    user_ids = set(
        SavedPrediction.objects.filter(prediction=pred).values_list("user_id", flat=True)
    )
    if not user_ids:
        return {"recipients": 0}

    icon = "✓" if pred.result == "won" else "✗" if pred.result == "lost" else "·"
    title = f"{icon} {pred.event.home_team.name} vs {pred.event.away_team.name}"
    body = f"Resultado: {pred.result.upper()} ({pred.market}/{pred.outcome} @ {pred.recommended_price})"
    data = {"kind": "prediction_settled", "prediction_id": pred.id, "result": pred.result}
    for uid in user_ids:
        send_push.delay(uid, "prediction_settled", title, body, data)
    return {"recipients": len(user_ids)}
