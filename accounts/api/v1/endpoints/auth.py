from rest_framework.permissions import AllowAny
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.api.v1.serializers.jwt import MyTokenObtainPairSerializer


class LoginView(TokenObtainPairView):
    """POST /api/v1/auth/token/

    Body: {username, password, provider, platform}
      - provider="password" (default): standard email+password
      - provider="google": password is the Google access_token (verified server-side)
      - provider="apple":  password is the Apple identity_token (verified server-side)
    """

    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [HasAPIKey]
    authentication_classes = []


class RefreshView(TokenRefreshView):
    """POST /api/v1/auth/token/refresh/  Body: {refresh}"""

    permission_classes = [AllowAny]
    authentication_classes = []


class VerifyView(TokenVerifyView):
    """POST /api/v1/auth/token/verify/  Body: {token}"""

    permission_classes = [HasAPIKey]
    authentication_classes = []
