"""Apple Sign-In token verification.

Apple sends an `id_token` (JWT) signed with their rotating ES256 keys. Verify by:
1. Fetching JWKS from https://appleid.apple.com/auth/keys
2. Picking the key matching the JWT `kid` header
3. Validating signature + iss=https://appleid.apple.com + aud=<client_id>

We do all of this with `pyjwt` (no Firebase SDK).
"""

from __future__ import annotations

import logging
from typing import Any

import jwt
import requests
from rest_framework.exceptions import AuthenticationFailed

from accounts.models.choices import ProviderAuthChoices
from accounts.social.shared import AuthProvider, get_user_by_email

logger = logging.getLogger(__name__)

APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"
# Set APPLE_CLIENT_ID env var to your bundle id / service id when you wire iOS auth.


class AppleAuthProvider(AuthProvider):
    def validate_token(self) -> dict[str, Any]:
        from django.conf import settings

        try:
            jwks = requests.get(APPLE_JWKS_URL, timeout=10).json()
        except Exception as exc:
            logger.warning("apple jwks fetch failed: %s", exc)
            raise AuthenticationFailed("apple_jwks_unreachable")

        try:
            unverified = jwt.get_unverified_header(self.token)
            kid = unverified.get("kid")
        except Exception:
            raise AuthenticationFailed("invalid_apple_token_header")

        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise AuthenticationFailed("apple_kid_not_found")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        audience = getattr(settings, "APPLE_CLIENT_ID", None)
        try:
            claims = jwt.decode(
                self.token,
                public_key,
                algorithms=["RS256"],
                audience=audience,
                issuer=APPLE_ISSUER,
            )
        except jwt.PyJWTError as exc:
            logger.info("apple token rejected: %s", exc)
            raise AuthenticationFailed("invalid_apple_token")
        return claims

    def get_user(self, ios: bool = False):
        try:
            data = self.validate_token()
        except AuthenticationFailed:
            return None, None
        email = data.get("email")
        if not email:
            return None, None
        return (
            get_user_by_email(
                email,
                provider=ProviderAuthChoices.APPLE,
                first_name=data.get("given_name", ""),
                last_name=data.get("family_name", ""),
            ),
            data,
        )
