from django.urls import include, path

from accounts.api.v1.endpoints.account import (
    AccountCreateView,
    AccountMeView,
    AccountVerifyEmailView,
)
from accounts.api.v1.endpoints.auth import LoginView, RefreshView, VerifyView
from accounts.api.v1.endpoints.profile import MeProfileView

app_name = "accounts"

urlpatterns = [
    # JWT obtain / refresh / verify
    path("token/", LoginView.as_view(), name="token-obtain"),
    path("token/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("token/verify/", VerifyView.as_view(), name="token-verify"),
    # Sign up + email verification
    path("account/create/", AccountCreateView.as_view(), name="account-create"),
    path(
        "account/verify/<str:uidb64>/<str:token>/",
        AccountVerifyEmailView.as_view(),
        name="account-verify",
    ),
    # Authenticated /me endpoints
    path("account/me/", AccountMeView.as_view(), name="account-me"),
    path("account/me/profile/", MeProfileView.as_view(), name="me-profile"),
    # Password reset (6-digit PIN, dlujo pattern)
    path("password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),
]
