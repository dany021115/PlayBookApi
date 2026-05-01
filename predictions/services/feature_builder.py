"""Build a FeatureVector payload for an Event from the local markets cache."""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from markets.models import Event, OddsSnapshot

CACHE_TTL = 5 * 60  # 5 min


def _serialize_snapshot(snap: OddsSnapshot) -> dict:
    return {
        "price": float(snap.price),
        "bookmaker_id": snap.bookmaker_id,
        "bookmaker_slug": snap.bookmaker.slug,
    }


def _market_odds_for_event(event: Event) -> dict[str, list[dict]]:
    """Return latest snapshot per (market, outcome, line, bookmaker)."""
    qs = (
        OddsSnapshot.objects.filter(event=event)
        .select_related("bookmaker")
        .order_by("-captured_at")
    )
    by_market: dict[str, dict[tuple, dict]] = defaultdict(dict)
    for snap in qs:
        line_key = float(snap.line) if snap.line is not None else None
        outcome_key = (snap.outcome, line_key)
        by_market[snap.market].setdefault(outcome_key, {
            "outcome": snap.outcome,
            "line": float(snap.line) if snap.line is not None else None,
            "snapshots": [],
            "_seen_bookmakers": set(),
        })
        entry = by_market[snap.market][outcome_key]
        if snap.bookmaker_id in entry["_seen_bookmakers"]:
            continue
        entry["_seen_bookmakers"].add(snap.bookmaker_id)
        entry["snapshots"].append(_serialize_snapshot(snap))

    out: dict[str, list[dict]] = {}
    for market, outcomes in by_market.items():
        rows = []
        for entry in outcomes.values():
            entry.pop("_seen_bookmakers", None)
            rows.append(entry)
        out[market] = rows
    return out


def _team_form(event: Event, team_id: int, last_n: int = 5) -> list[str]:
    cutoff = event.start_time
    qs = (
        Event.objects.filter(
            status=Event.Status.FINISHED,
            start_time__lt=cutoff,
            home_score__isnull=False, away_score__isnull=False,
        )
        .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
        .order_by("-start_time")[:last_n]
    )
    out: list[str] = []
    for ev in qs:
        if ev.home_score is None or ev.away_score is None:
            continue
        if ev.home_team_id == team_id:
            mine, theirs = ev.home_score, ev.away_score
        else:
            mine, theirs = ev.away_score, ev.home_score
        if mine > theirs:
            out.append("W")
        elif mine == theirs:
            out.append("D")
        else:
            out.append("L")
    return out


def _avg_goals(event: Event, team_id: int, last_n: int = 10) -> float:
    cutoff = event.start_time
    qs = (
        Event.objects.filter(
            status=Event.Status.FINISHED,
            start_time__lt=cutoff,
            home_score__isnull=False, away_score__isnull=False,
        )
        .filter(Q(home_team_id=team_id) | Q(away_team_id=team_id))
        .order_by("-start_time")[:last_n]
    )
    goals = []
    for ev in qs:
        goals.append(ev.home_score if ev.home_team_id == team_id else ev.away_score)
    return round(sum(goals) / len(goals), 2) if goals else 0.0


def _h2h(event: Event, last_n: int = 3) -> list[dict]:
    qs = (
        Event.objects.filter(
            status=Event.Status.FINISHED,
            home_score__isnull=False, away_score__isnull=False,
        )
        .filter(
            Q(home_team=event.home_team, away_team=event.away_team)
            | Q(home_team=event.away_team, away_team=event.home_team)
        )
        .order_by("-start_time")[:last_n]
    )
    return [
        {
            "date": ev.start_time.date().isoformat(),
            "home": ev.home_team.name,
            "away": ev.away_team.name,
            "score": f"{ev.home_score}-{ev.away_score}",
        }
        for ev in qs
    ]


def build_features(event: Event) -> dict[str, Any]:
    """Cached feature builder. TTL CACHE_TTL seconds per event."""
    key = f"features:event:{event.id}"
    cached = cache.get(key)
    if cached:
        return cached

    payload = {
        "event_id": event.id,
        "captured_at": timezone.now().isoformat(),
        "form": {
            "home": _team_form(event, event.home_team_id),
            "away": _team_form(event, event.away_team_id),
        },
        "avg_goals": {
            "home": _avg_goals(event, event.home_team_id),
            "away": _avg_goals(event, event.away_team_id),
        },
        "h2h": _h2h(event),
        "market_odds": _market_odds_for_event(event),
    }
    cache.set(key, payload, timeout=CACHE_TTL)
    return payload
