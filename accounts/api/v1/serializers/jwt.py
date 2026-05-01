"""TokenObtainPairSerializer with multi-provider auth (password / google / apple).

Pattern from /Users/quasar/Documents/GitHub/dlujo/api/main/api/serializers/jwt.py.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.api.v1.serializers.user import UserSerializer
from accounts.models.choices import PlatformChoices, ProviderAuthChoices
from accounts.social.apple import AppleAuthProvider
from accounts.social.google import GoogleAuthProvider


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    provider = serializers.CharField(required=False, default="password")
    platform = serializers.CharField(required=False, default="unknown")

    default_error_messages = {
        "no_active_account": _("No active account found with the given credentials"),
    }

    @staticmethod
    def _get_provider(attrs):
        try:
            return ProviderAuthChoices(attrs.get("provider", "password"))
        except ValueError:
            raise AuthenticationFailed("invalid_provider")

    @staticmethod
    def _get_platform(attrs):
        try:
            return PlatformChoices(attrs.get("platform", "unknown"))
        except ValueError:
            return None

    @staticmethod
    def _get_auth_provider(provider: ProviderAuthChoices, token: str):
        if provider == ProviderAuthChoices.GOOGLE:
            return GoogleAuthProvider(token)
        if provider == ProviderAuthChoices.APPLE:
            return AppleAuthProvider(token)
        raise AuthenticationFailed("invalid_provider")

    def validate(self, attrs):
        provider = self._get_provider(attrs)
        platform = self._get_platform(attrs)
        password = attrs.get("password")

        if provider == ProviderAuthChoices.PASSWORD:
            super().validate(attrs)
            return self._build_response(self.user)

        auth_provider = self._get_auth_provider(provider, password)
        user, userinfo = auth_provider.get_user(ios=(platform == PlatformChoices.IOS))
        if not user or not userinfo:
            raise AuthenticationFailed(self.error_messages["no_active_account"], "no_active_account")
        return self._build_response(user)

    def _build_response(self, user):
        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }
