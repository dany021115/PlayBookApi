"""Health check endpoints — liveness + readiness probes."""

import logging

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class LivenessCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "alive"})


class ReadinessCheckView(APIView):
    """Check DB + cache + Celery broker + sports-odds-api + LLM provider."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        health = {"status": "healthy", "checks": {}}

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            health["checks"]["database"] = {"status": "healthy"}
        except Exception as exc:
            logger.error("DB health failed: %s", exc)
            health["checks"]["database"] = {"status": "unhealthy", "error": str(exc)}
            health["status"] = "unhealthy"

        try:
            cache.set("health_check", "ok", timeout=10)
            if cache.get("health_check") != "ok":
                raise Exception("cache mismatch")
            cache.delete("health_check")
            health["checks"]["cache"] = {"status": "healthy"}
        except Exception as exc:
            logger.error("Cache health failed: %s", exc)
            health["checks"]["cache"] = {"status": "unhealthy", "error": str(exc)}
            health["status"] = "unhealthy"

        try:
            from PlayBookApi.celery import app as celery_app

            conn = celery_app.connection()
            conn.ensure_connection(max_retries=1, timeout=5)
            conn.release()
            health["checks"]["celery_broker"] = {"status": "healthy"}
        except Exception as exc:
            logger.warning("Celery broker health failed: %s", exc)
            health["checks"]["celery_broker"] = {"status": "unhealthy", "error": str(exc)}
            health["status"] = "unhealthy"

        sports_url = getattr(settings, "SPORTS_ODDS_API_URL", "")
        if sports_url:
            try:
                resp = requests.get(f"{sports_url}/health/live/", timeout=3)
                if resp.status_code == 200:
                    health["checks"]["sports_odds_api"] = {"status": "healthy"}
                else:
                    raise Exception(f"HTTP {resp.status_code}")
            except Exception as exc:
                logger.warning("sports-odds-api unreachable: %s", exc)
                health["checks"]["sports_odds_api"] = {"status": "unhealthy", "error": str(exc)}
                # Don't flip overall to unhealthy — sports-odds-api downtime is expected to be tolerable
        else:
            health["checks"]["sports_odds_api"] = {"status": "skipped", "reason": "URL unset"}

        if getattr(settings, "LLM_API_KEY", ""):
            health["checks"]["llm"] = {"status": "configured", "provider": settings.LLM_PROVIDER}
        else:
            health["checks"]["llm"] = {"status": "skipped", "reason": "no LLM_API_KEY"}

        status_code = 200 if health["status"] == "healthy" else 503
        return Response(health, status=status_code)
