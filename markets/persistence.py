"""Idempotent upserts from sports-odds-api JSON into local markets cache."""

from __future__ import annotations

import logging
from typing import Any

from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from markets.models import Bookmaker, Event, League, OddsSnapshot, Sport, Team

logger = logging.getLogger(__name__)


def _parse_dt(value: Any):
    if not value:
        return None
    if hasattr(value, "isoformat"):
        return value
    return parse_datetime(value)


def upsert_sport(key: str) -> Sport:
    key_l = (key or "").lower().strip()
    obj, _ = Sport.objects.get_or_create(
        key=key_l,
        defaults={"name": key_l.title(), "slug": slugify(key_l) or key_l},
    )
    return obj


def upsert_league(sport: Sport, name: str, country: str = "") -> League:
    base = f"{country}-{name}" if country else name
    slug = (slugify(base) or "league")[:180]
    obj, _ = League.objects.get_or_create(
        sport=sport, slug=slug,
        defaults={"name": name or slug, "country": country or ""},
    )
    return obj


def upsert_team(league: League, name: str) -> Team:
    if not name:
        return None  # type: ignore[return-value]
    slug = (slugify(name) or "team")[:180]
    obj, _ = Team.objects.get_or_create(
        league=league, slug=slug,
        defaults={"name": name},
    )
    return obj


def upsert_event_from_upstream(payload: dict[str, Any]) -> Event | None:
    """Upsert a markets.Event from a sports-odds-api `/api/matches/` row."""
    upstream_id = payload.get("id")
    if not upstream_id:
        return None
    sport_key = payload.get("sport") or ""
    league_name = payload.get("league") or ""
    home_name = payload.get("home_team") or ""
    away_name = payload.get("away_team") or ""
    start_time = _parse_dt(payload.get("start_time"))
    if not (sport_key and league_name and home_name and away_name and start_time):
        return None

    sport = upsert_sport(sport_key)
    league = upsert_league(sport, league_name)
    home = upsert_team(league, home_name)
    away = upsert_team(league, away_name)
    if not home or not away:
        return None

    defaults = {
        "league": league,
        "home_team": home,
        "away_team": away,
        "status": payload.get("status") or Event.Status.SCHEDULED,
        "start_time": start_time,
        "home_score": payload.get("home_score"),
        "away_score": payload.get("away_score"),
        "minute": payload.get("minute") or "",
        "upstream_updated_at": _parse_dt(payload.get("updated_at")),
    }
    obj, created = Event.objects.update_or_create(
        upstream_id=upstream_id, defaults=defaults,
    )
    return obj


def upsert_bookmaker(slug: str) -> Bookmaker:
    s = (slugify(slug) or "unknown")[:60]
    obj, _ = Bookmaker.objects.get_or_create(
        slug=s, defaults={"name": (slug or "unknown").replace("_", " ").title()[:80]},
    )
    return obj


def upsert_odds_from_upstream(payload: dict[str, Any]) -> OddsSnapshot | None:
    """Upsert a markets.OddsSnapshot from a sports-odds-api `/api/odds/...` row."""
    upstream_id = payload.get("id")
    event_upstream_id = payload.get("event_id")
    if not upstream_id or not event_upstream_id:
        return None

    event = Event.objects.filter(upstream_id=event_upstream_id).first()
    if not event:
        # Caller should have synced events first; skip orphans.
        return None

    bookmaker = upsert_bookmaker(payload.get("bookmaker") or "unknown")
    captured_at = _parse_dt(payload.get("captured_at"))
    if not captured_at:
        return None

    obj, _ = OddsSnapshot.objects.update_or_create(
        upstream_id=upstream_id,
        defaults={
            "event": event,
            "bookmaker": bookmaker,
            "market": payload.get("market") or "",
            "outcome": (payload.get("outcome") or "").strip().lower()[:40],
            "line": payload.get("line"),
            "price": payload.get("price") or 0,
            "captured_at": captured_at,
        },
    )
    return obj
