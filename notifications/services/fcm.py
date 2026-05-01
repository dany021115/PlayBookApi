"""FCM HTTP v1 client. No firebase_admin SDK (Cuba-friendly).

Uses google-auth (already a dep) to get an OAuth2 token from a service account
JSON file, then POSTs to https://fcm.googleapis.com/v1/projects/<project>/messages:send.
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"


def _get_access_token() -> str | None:
    path = getattr(settings, "FCM_SERVICE_ACCOUNT_PATH", "") or ""
    if not path:
        return None
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request as GoogleRequest
    except ImportError:
        logger.warning("google-auth not available")
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(
            path, scopes=[FCM_SCOPE],
        )
        creds.refresh(GoogleRequest())
        return creds.token
    except Exception as exc:
        logger.warning("FCM access token failed: %s", exc)
        return None


def send_to_token(token: str, title: str, body: str, data: dict[str, Any] | None = None) -> tuple[bool, str, str]:
    """Returns (success, message_id_or_empty, error_or_empty)."""
    access = _get_access_token()
    if not access:
        return False, "", "no_access_token"
    project_id = getattr(settings, "FCM_PROJECT_ID", "") or ""
    if not project_id:
        return False, "", "no_fcm_project_id"

    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    payload = {
        "message": {
            "token": token,
            "notification": {"title": title, "body": body},
            "data": {k: str(v) for k, v in (data or {}).items()},
        }
    }
    try:
        resp = requests.post(url, json=payload,
                             headers={"Authorization": f"Bearer {access}",
                                      "Content-Type": "application/json"},
                             timeout=10)
    except Exception as exc:
        return False, "", str(exc)
    if resp.status_code != 200:
        return False, "", f"HTTP {resp.status_code}: {resp.text[:300]}"
    return True, resp.json().get("name", ""), ""
