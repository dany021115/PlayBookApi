"""Unfold admin dashboard callback. Filled in Fase 7."""

import json
from datetime import timedelta

from django.utils import timezone


def dashboard_callback(request, context):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    _j = json.dumps

    # Lazy imports — apps may not be ready in early phases
    kpi = {}
    try:
        from accounts.models import Profile
        from django.contrib.auth import get_user_model

        User = get_user_model()
        kpi["users_total"] = User.objects.count()
        kpi["users_signups_7d"] = User.objects.filter(date_joined__gte=week_ago).count()
        kpi["profiles_total"] = Profile.objects.count()
    except Exception:
        kpi.update({"users_total": 0, "users_signups_7d": 0, "profiles_total": 0})

    try:
        from markets.models import Event

        kpi["events_total"] = Event.objects.count()
        kpi["events_scheduled"] = Event.objects.filter(status="scheduled").count()
        kpi["events_live"] = Event.objects.filter(status="live").count()
    except Exception:
        kpi.update({"events_total": 0, "events_scheduled": 0, "events_live": 0})

    try:
        from predictions.models import Prediction

        kpi["predictions_total"] = Prediction.objects.count()
        kpi["predictions_pending"] = Prediction.objects.filter(status="pending").count()
        kpi["predictions_won_7d"] = Prediction.objects.filter(
            settled_at__gte=week_ago, result="won"
        ).count()
        kpi["predictions_lost_7d"] = Prediction.objects.filter(
            settled_at__gte=week_ago, result="lost"
        ).count()
        won, lost = kpi["predictions_won_7d"], kpi["predictions_lost_7d"]
        kpi["hit_rate_7d"] = round(won / (won + lost) * 100, 1) if (won + lost) else 0
    except Exception:
        kpi.update({
            "predictions_total": 0, "predictions_pending": 0,
            "predictions_won_7d": 0, "predictions_lost_7d": 0, "hit_rate_7d": 0,
        })

    context.update({
        **kpi,
        "trend_json": _j({"labels": [], "values": []}),
    })
    return context
