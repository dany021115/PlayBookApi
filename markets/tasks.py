"""Celery tasks: keep markets cache in sync with sports-odds-api."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from celery import shared_task
from django.utils import timezone

from markets.client import SportsOddsClient
from markets.persistence import (
    upsert_event_from_upstream,
    upsert_odds_from_upstream,
)

logger = logging.getLogger(__name__)


def _run_async(coro):
    return asyncio.run(coro)


async def _fetch_window(start_after: str | None = None,
                        start_before: str | None = None,
                        status: str | None = None) -> list[dict[str, Any]]:
    async with SportsOddsClient() as client:
        return await client.list_matches(
            status=status, start_after=start_after, start_before=start_before,
        )


@shared_task(name="markets.tasks.refresh_upcoming_events", bind=True, max_retries=2,
             default_retry_delay=60)
def refresh_upcoming_events(self, hours_ahead: int = 720) -> dict[str, int]:
    """Pull scheduled events for next `hours_ahead` hours and upsert. Default 30 days."""
    now = timezone.now()
    start_after = now.isoformat()
    start_before = (now + timedelta(hours=hours_ahead)).isoformat()
    try:
        items = _run_async(_fetch_window(start_after=start_after, start_before=start_before,
                                         status="scheduled"))
    except Exception as exc:
        logger.error("refresh_upcoming_events failed: %s", exc)
        raise self.retry(exc=exc)
    upserted = 0
    for item in items:
        try:
            if upsert_event_from_upstream(item):
                upserted += 1
        except Exception as exc:
            logger.warning("upsert event failed (%s): %s", item.get("id"), exc)
    logger.info("refresh_upcoming_events: %d/%d events", upserted, len(items))
    return {"fetched": len(items), "upserted": upserted}


@shared_task(name="markets.tasks.refresh_finished_events", bind=True, max_retries=2,
             default_retry_delay=60)
def refresh_finished_events(self, hours_back: int = 168) -> dict[str, int]:
    """Pull recently finished events so settlement can run. Default 7 days back."""
    now = timezone.now()
    start_after = (now - timedelta(hours=hours_back)).isoformat()
    try:
        items = _run_async(_fetch_window(start_after=start_after, status="finished"))
    except Exception as exc:
        logger.error("refresh_finished_events failed: %s", exc)
        raise self.retry(exc=exc)
    upserted = 0
    for item in items:
        try:
            if upsert_event_from_upstream(item):
                upserted += 1
        except Exception as exc:
            logger.warning("upsert event failed (%s): %s", item.get("id"), exc)
    logger.info("refresh_finished_events: %d/%d events", upserted, len(items))
    return {"fetched": len(items), "upserted": upserted}


@shared_task(name="markets.tasks.refresh_live_events", bind=True, max_retries=2,
             default_retry_delay=30)
def refresh_live_events(self) -> dict[str, int]:
    try:
        items = _run_async(_fetch_window(status="live"))
    except Exception as exc:
        logger.error("refresh_live_events failed: %s", exc)
        raise self.retry(exc=exc)
    upserted = 0
    for item in items:
        try:
            if upsert_event_from_upstream(item):
                upserted += 1
        except Exception as exc:
            logger.warning("upsert event failed (%s): %s", item.get("id"), exc)
    return {"fetched": len(items), "upserted": upserted}


async def _fetch_odds(sport: str) -> list[dict[str, Any]]:
    async with SportsOddsClient() as client:
        return await client.list_odds_for_sport(sport)


@shared_task(name="markets.tasks.refresh_odds", bind=True, max_retries=2,
             default_retry_delay=30)
def refresh_odds(self, sport: str = "football") -> dict[str, int]:
    try:
        items = _run_async(_fetch_odds(sport))
    except Exception as exc:
        logger.error("refresh_odds(%s) failed: %s", sport, exc)
        raise self.retry(exc=exc)
    upserted = 0
    skipped = 0
    for item in items:
        try:
            if upsert_odds_from_upstream(item):
                upserted += 1
            else:
                skipped += 1
        except Exception as exc:
            logger.warning("upsert odds failed (%s): %s", item.get("id"), exc)
    return {"sport": sport, "fetched": len(items), "upserted": upserted, "skipped": skipped}
