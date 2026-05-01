"""Audit log middleware: captures /api/v1/* mutations into AuditLog."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SCOPED_PREFIX = "/api/v1/"

# Don't log auth bodies (passwords, tokens) verbatim
SENSITIVE_KEYS = {"password", "current_password", "new_password", "token", "refresh", "access"}
MAX_BODY_BYTES = 4096


def _client_ip(request) -> str:
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _safe_payload(raw: bytes) -> dict[str, Any]:
    if not raw:
        return {}
    if len(raw) > MAX_BODY_BYTES:
        return {"_truncated": True, "_size": len(raw)}
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        return {"_non_json": True}
    if isinstance(data, dict):
        return {k: ("***" if k in SENSITIVE_KEYS else v) for k, v in data.items()}
    return {"_payload": data}


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        captured_body = b""
        if request.method in MUTATING_METHODS and request.path.startswith(SCOPED_PREFIX):
            try:
                captured_body = request.body
            except Exception:
                captured_body = b""

        response = self.get_response(request)
        try:
            self._log(request, response, captured_body, time.monotonic() - start)
        except Exception as exc:
            logger.warning("AuditLogMiddleware failed: %s", exc)
        return response

    def _log(self, request, response, body: bytes, elapsed: float):
        if request.method not in MUTATING_METHODS:
            return
        if not request.path.startswith(SCOPED_PREFIX):
            return
        from compliance.models.audit_log import AuditLog

        user = request.user if hasattr(request, "user") and request.user.is_authenticated else None
        AuditLog.objects.create(
            user=user,
            method=request.method,
            path=request.path[:512],
            status_code=getattr(response, "status_code", 0),
            ip_address=_client_ip(request)[:64],
            user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:512],
            request_payload=_safe_payload(body),
            response_summary={"status_code": getattr(response, "status_code", 0)},
            duration_ms=int(elapsed * 1000),
        )
