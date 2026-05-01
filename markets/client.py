"""Async HTTP client for sports-odds-api.

Signs every request with a fresh internal JWT (PlayBookApi → sports-odds-api).
Implements retry with exponential backoff and a circuit-breaker via Redis cache.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from django.conf import settings
from django.core.cache import cache

from PlayBookApi.security import auth_headers

logger = logging.getLogger(__name__)

CIRCUIT_BREAKER_KEY = "sports_odds_down"
CIRCUIT_BREAKER_TTL = 30  # seconds — pause requests if breaker tripped


class SportsOddsClient:
    """Thin async HTTP client. One instance per async context (use `async with`)."""

    def __init__(self, base_url: str | None = None, *, timeout: float = 15.0) -> None:
        self._base_url = base_url or settings.SPORTS_ODDS_API_URL
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "SportsOddsClient":
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client is not None:
            await self._client.aclose()

    async def _get(self, path: str, params: dict[str, Any] | None = None,
                   *, retries: int = 3, paginate: bool = False) -> dict[str, Any] | list[Any]:
        """GET with auth + retry. Raises httpx.HTTPError on final failure."""
        if cache.get(CIRCUIT_BREAKER_KEY):
            logger.warning("sports-odds-api circuit breaker open; refusing %s", path)
            raise RuntimeError("sports_odds_circuit_open")

        assert self._client is not None, "use async with SportsOddsClient(): ..."
        attempt = 0
        while True:
            try:
                resp = await self._client.get(path, params=params, headers=auth_headers())
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in (401, 403):
                    raise  # auth bug — don't retry
                if attempt >= retries:
                    cache.set(CIRCUIT_BREAKER_KEY, "1", timeout=CIRCUIT_BREAKER_TTL)
                    raise
            except httpx.HTTPError:
                if attempt >= retries:
                    cache.set(CIRCUIT_BREAKER_KEY, "1", timeout=CIRCUIT_BREAKER_TTL)
                    raise
            await asyncio.sleep(2 ** attempt)
            attempt += 1

    async def _get_paginated(self, path: str, params: dict[str, Any] | None = None,
                             *, max_pages: int = 50) -> list[dict[str, Any]]:
        """Walk DRF cursor/limit-offset pagination, return flat results list."""
        all_items: list[dict[str, Any]] = []
        next_path = path
        next_params = dict(params or {})
        next_params.setdefault("limit", 100)
        for _ in range(max_pages):
            data = await self._get(next_path, next_params)
            if isinstance(data, list):
                all_items.extend(data)
                return all_items
            results = data.get("results", []) if isinstance(data, dict) else []
            all_items.extend(results)
            nxt = data.get("next") if isinstance(data, dict) else None
            if not nxt:
                return all_items
            # Strip base url to keep relative path for next iteration
            if nxt.startswith(self._base_url):
                nxt = nxt[len(self._base_url):]
            next_path = nxt
            next_params = None
        logger.warning("paginated fetch hit max_pages=%d for %s", max_pages, path)
        return all_items

    # ── Domain shortcuts ──

    async def list_sports(self) -> list[dict[str, Any]]:
        data = await self._get("/api/sports/")
        return data if isinstance(data, list) else data.get("results", [])

    async def list_matches(self, *, status: str | None = None,
                           sport: str | None = None,
                           start_after: str | None = None,
                           start_before: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if status:
            params["status"] = status
        if sport:
            params["sport"] = sport
        if start_after:
            params["start_after"] = start_after
        if start_before:
            params["start_before"] = start_before
        return await self._get_paginated("/api/matches/", params)

    async def get_match(self, match_id: int) -> dict[str, Any]:
        return await self._get(f"/api/matches/{match_id}/")

    async def list_odds_for_sport(self, sport: str, *, market: str | None = None,
                                  bookmaker: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if market:
            params["market"] = market
        if bookmaker:
            params["bookmaker"] = bookmaker
        return await self._get_paginated(f"/api/odds/{sport}/", params)

    async def list_odds_for_event(self, event_id: int) -> list[dict[str, Any]]:
        data = await self._get(f"/api/odds/event/{event_id}/")
        return data if isinstance(data, list) else data.get("results", [])
