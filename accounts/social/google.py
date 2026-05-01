"""Google OAuth — verify access token via /oauth2/v3/userinfo (Cuba-friendly).

Pattern: /Users/quasar/Documents/GitHub/dlujo/api/main/social/google.py
No Firebase SDK. Plain HTTP to Google's public userinfo endpoint, which works
where Firebase is geo-blocked.
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from rest_framework.exceptions import AuthenticationFailed

from accounts.models.choices import ProviderAuthChoices
from accounts.social.shared import AuthProvider, get_user_by_email

logger = logging.getLogger(__name__)

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleAuthProvider(AuthProvider):
    def validate_token(self) -> dict[str, Any]:
        try:
            r = requests.get(
                GOOGLE_USERINFO_URL,
                params={"access_token": self.token},
                timeout=10,
            )
        except requests.RequestException as exc:
            logger.warning("google userinfo request failed: %s", exc)
            raise AuthenticationFailed("google_unreachable")
        if not r.ok:
            logger.info("google userinfo rejected token: %s", r.status_code)
            raise AuthenticationFailed("invalid_google_token")
        return r.json()

    def get_user(self, ios: bool = False):
        try:
            data = self.validate_token()
        except AuthenticationFailed:
            return None, None
        email = data.get("email")
        if not email:
            return None, None
        user = get_user_by_email(
            email,
            provider=ProviderAuthChoices.GOOGLE,
            first_name=data.get("given_name", ""),
            last_name=data.get("family_name", ""),
        )
        return user, data
