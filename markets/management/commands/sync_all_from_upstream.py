"""Full backfill of markets cache from sports-odds-api.

Fetches everything via async HTTP, then processes DB writes synchronously
(Django ORM doesn't allow sync ops inside an async context).
"""

from __future__ import annotations

import asyncio
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from markets.client import SportsOddsClient
from markets.models import Sport
from markets.persistence import (
    upsert_event_from_upstream,
    upsert_odds_from_upstream,
)

DEFAULT_SPORTS_FOR_ODDS = ["football", "basketball", "baseball", "ice-hockey"]


class Command(BaseCommand):
    help = "Full sync of sports/events/odds from sports-odds-api into local markets cache."

    def add_arguments(self, parser):
        parser.add_argument("--past-days", type=int, default=14)
        parser.add_argument("--future-days", type=int, default=30)
        parser.add_argument("--skip-odds", action="store_true")
        parser.add_argument("--sports", nargs="+", default=DEFAULT_SPORTS_FOR_ODDS)

    def handle(self, *args, past_days, future_days, skip_odds, sports, **opts):
        fetched = asyncio.run(self._fetch_all(past_days, future_days, skip_odds, sports))

        out: dict[str, int] = {}

        for s in fetched["sports"]:
            key = (s.get("key") or "").lower().strip()
            if not key:
                continue
            Sport.objects.get_or_create(
                key=key,
                defaults={
                    "name": s.get("name") or key.title(),
                    "slug": s.get("slug") or slugify(key),
                },
            )
        out["sports"] = Sport.objects.count()

        for status, items in fetched["events"].items():
            upserted = 0
            for it in items:
                try:
                    if upsert_event_from_upstream(it):
                        upserted += 1
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(
                        f"  upsert_event {it.get('id')} failed: {exc}"
                    ))
            out[f"events_{status}"] = upserted
            self.stdout.write(f"  events[{status}]: {upserted}/{len(items)}")

        for sport, items in fetched["odds"].items():
            upserted = 0
            skipped = 0
            for it in items:
                try:
                    if upsert_odds_from_upstream(it):
                        upserted += 1
                    else:
                        skipped += 1
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(
                        f"  upsert_odds {it.get('id')} failed: {exc}"
                    ))
                    skipped += 1
            out[f"odds_{sport}"] = upserted
            self.stdout.write(f"  odds[{sport}]: {upserted} upserted, {skipped} orphans")

        self.stdout.write(self.style.SUCCESS(f"Done: {out}"))

    async def _fetch_all(self, past_days, future_days, skip_odds, sports):
        result = {"sports": [], "events": {"scheduled": [], "live": [], "finished": []}, "odds": {}}
        async with SportsOddsClient() as client:
            try:
                result["sports"] = await client.list_sports()
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"sports list failed: {exc}"))

            now = timezone.now()
            start_after = (now - timedelta(days=past_days)).isoformat()
            start_before = (now + timedelta(days=future_days)).isoformat()
            self.stdout.write(f"Window: {start_after} → {start_before}")

            for status in ("scheduled", "live", "finished"):
                try:
                    items = await client.list_matches(
                        status=status,
                        start_after=start_after,
                        start_before=start_before,
                    )
                    result["events"][status] = items
                    self.stdout.write(f"  fetched {status}: {len(items)} items")
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f"matches[{status}] fetch failed: {exc}"))

            if not skip_odds:
                for sport in sports:
                    try:
                        items = await client.list_odds_for_sport(sport)
                        result["odds"][sport] = items
                        self.stdout.write(f"  fetched odds[{sport}]: {len(items)} items")
                    except Exception as exc:
                        self.stdout.write(self.style.WARNING(f"odds[{sport}] fetch failed: {exc}"))

        return result
