"""Pytest fixtures for PlayBookApi tests.

Patterns inspired by:
  /Users/quasar/Documents/GitHub/dlujo/api/conftest.py (api_key fixture)
  /Users/quasar/Documents/GitHub/TeeShot/TeeShotApi/conftest.py (authenticated_client)
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


MOCK_GOOGLE_USERINFO = {
    "sub": "google-uid-123",
    "email": "test@example.com",
    "email_verified": True,
    "given_name": "Test",
    "family_name": "User",
    "name": "Test User",
    "picture": "",
    "locale": "es",
}


@pytest.fixture
def mock_google_userinfo():
    """Patch the Google userinfo HTTP call so token validation never hits the network."""
    with patch("accounts.social.google.requests.get") as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = MOCK_GOOGLE_USERINFO
        yield mock_get


@pytest.fixture
def api_key(db):
    from rest_framework_api_key.models import APIKey

    _, key = APIKey.objects.create_key(name="test-flutter-app")
    return key


@pytest.fixture
def authenticated_client(db, api_client, api_key, mock_google_userinfo):
    """Authenticated DRF client (Google login + API key) for a fresh test user."""
    api_client.credentials(HTTP_X_API_KEY=api_key)
    resp = api_client.post(
        "/api/v1/auth/token/",
        {
            "username": "",
            "password": "fake-google-access-token",
            "provider": "google",
            "platform": "ANDROID",
        },
        format="json",
    )
    assert resp.status_code == 200, resp.content
    data = resp.json()
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {data['access']}",
        HTTP_X_API_KEY=api_key,
    )
    return api_client
