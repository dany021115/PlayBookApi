from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from PlayBookApi.health import LivenessCheckView, ReadinessCheckView
from PlayBookApi.views import APIVersionView

urlpatterns = [
    path("", APIVersionView.as_view(), name="api-version"),
    path("admin/", admin.site.urls),
    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Health
    path("health/live/", LivenessCheckView.as_view(), name="health-liveness"),
    path("health/ready/", ReadinessCheckView.as_view(), name="health-readiness"),
    # Apps
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/markets/", include("markets.urls")),
    path("api/v1/", include("predictions.urls")),
    path("api/v1/", include("follows.urls")),
    path("api/v1/", include("notifications.urls")),
]
