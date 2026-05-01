"""Outbound JWT issuance for calling sports-odds-api server-to-server.

The main backend (this service) and sports-odds-api share the SAME map of
{kid: secret} via env (`SPORTS_ODDS_JWT_KEYS`). PlayBookApi signs short-lived
tokens with the active kid; sports-odds-api accepts any kid present in its map.

Rotation:
    1. Generate new (kid, secret) and add to BOTH services' env.
    2. Restart both — both accept old + new.
    3. Switch SPORTS_ODDS_JWT_ACTIVE_KID here to the new kid.
    4. After old tokens TTL expires, remove old kid from both.
"""

from __future__ import annotations

import time
from typing import Any

import jwt
from django.conf import settings


def issue_internal_token(*, ttl_seconds: int | None = None) -> str:
    """Sign a fresh JWT for calling sports-odds-api. Default TTL from settings."""
    keys = getattr(settings, "SPORTS_ODDS_JWT_KEYS", {}) or {}
    kid = getattr(settings, "SPORTS_ODDS_JWT_ACTIVE_KID", "")
    if not keys or kid not in keys:
        raise RuntimeError(
            "SPORTS_ODDS_JWT_KEYS is unset or missing active kid. "
            "Configure env to call sports-odds-api."
        )
    secret = keys[kid]
    now = int(time.time())
    ttl = int(ttl_seconds or getattr(settings, "SPORTS_ODDS_JWT_TTL_SECONDS", 60))
    payload: dict[str, Any] = {
        "iss": getattr(settings, "SPORTS_ODDS_JWT_ISS", "playbook-api"),
        "aud": getattr(settings, "SPORTS_ODDS_JWT_AUD", "sports-odds-api"),
        "iat": now,
        "exp": now + ttl,
        "sub": "playbook-svc",
    }
    return jwt.encode(
        payload,
        secret,
        algorithm=getattr(settings, "SPORTS_ODDS_JWT_ALG", "HS256"),
        headers={"kid": kid},
    )


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {issue_internal_token()}"}
