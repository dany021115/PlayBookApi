"""OAuth provider abstractions. Pattern from /Users/quasar/Documents/GitHub/dlujo/api/main/social/shared.py."""

from __future__ import annotations

import random
import string
from abc import ABC, abstractmethod
from typing import Any

from django.contrib.auth import get_user_model

from accounts.models import Profile
from accounts.models.choices import ProviderAuthChoices

User = get_user_model()


class AuthProvider(ABC):
    def __init__(self, token: str):
        self.token = token

    @abstractmethod
    def validate_token(self) -> dict[str, Any]:
        """Validates the token via the provider's userinfo endpoint, returns claims."""

    @abstractmethod
    def get_user(self, ios: bool = False) -> tuple["User | None", dict[str, Any] | None]:
        """Returns (User, claims). On failure, (None, None)."""


def _generate_random_suffix(length: int = 5) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_user_by_email(email: str, provider: ProviderAuthChoices, **defaults: Any):
    """Find user by email or create one. Ensures Profile exists with the provider tag."""
    if not email:
        return None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        username = email
        if User.objects.filter(username=username).exists():
            while True:
                alt = f"{_generate_random_suffix()}_{username}"
                if not User.objects.filter(username=alt).exists():
                    username = alt
                    break
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": email, **defaults},
        )

    profile, _ = Profile.objects.get_or_create(user=user)
    if not profile.provider:
        profile.provider = provider.value if hasattr(provider, "value") else str(provider)
        profile.save(update_fields=["provider"])
    return user
