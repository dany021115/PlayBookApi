"""WebSocket consumer that proxies upstream SSE to Flutter clients.

Flutter connects to ws://api/ws/matches/?sport=football&token=<JWT>.
This consumer authenticates the token, opens an SSE connection upstream
to sports-odds-api/api/stream/matches/?sport=football, parses each
`event: match` block and forwards JSON to the WebSocket client.
"""

from __future__ import annotations

import asyncio
import json
import logging
from urllib.parse import parse_qs

import httpx
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from PlayBookApi.security import auth_headers

logger = logging.getLogger(__name__)


class MatchStreamConsumer(AsyncWebsocketConsumer):
    upstream_task: asyncio.Task | None = None

    async def connect(self):
        # Auth via querystring ?token=<jwt>
        qs = parse_qs(self.scope.get("query_string", b"").decode())
        token = (qs.get("token") or [""])[0]
        if not token:
            await self.close(code=4401)
            return
        try:
            AccessToken(token)
        except (InvalidToken, TokenError):
            await self.close(code=4401)
            return

        await self.accept()
        sport = (qs.get("sport") or [""])[0]
        url = f"{settings.SPORTS_ODDS_API_URL}/api/stream/matches/"
        if sport:
            url += f"?sport={sport}"
        self.upstream_task = asyncio.create_task(self._proxy_sse(url))

    async def disconnect(self, close_code):
        if self.upstream_task:
            self.upstream_task.cancel()

    async def _proxy_sse(self, url: str):
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", url, headers=auth_headers()) as resp:
                    if resp.status_code != 200:
                        await self.send(text_data=json.dumps(
                            {"type": "error", "status": resp.status_code}
                        ))
                        return
                    event_name = "message"
                    data_lines: list[str] = []
                    async for raw_line in resp.aiter_lines():
                        if not raw_line:
                            if data_lines:
                                payload = "\n".join(data_lines)
                                await self.send(text_data=json.dumps(
                                    {"type": event_name, "data": payload}
                                ))
                                data_lines = []
                                event_name = "message"
                            continue
                        if raw_line.startswith(":"):
                            continue  # SSE comment / heartbeat
                        if raw_line.startswith("event:"):
                            event_name = raw_line[6:].strip()
                        elif raw_line.startswith("data:"):
                            data_lines.append(raw_line[5:].lstrip())
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("SSE proxy crashed: %s", exc)
            try:
                await self.send(text_data=json.dumps({"type": "error", "error": str(exc)}))
            except Exception:
                pass
