"""ASGI config — HTTP + WebSocket via Channels.

WebSocket auth: JWT in querystring (`?token=...`) handled by SimpleJWTAuthMiddleware
defined later when the auth app is ready. For Fase 0 we keep it minimal.
"""

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PlayBookApi.settings")
django.setup()

http_app = get_asgi_application()


def _websocket_urlpatterns():
    """Lazy-import so app autoload order doesn't break asgi at boot."""
    patterns = []
    try:
        from markets.routing import websocket_urlpatterns as markets_ws

        patterns.extend(markets_ws)
    except Exception:
        pass
    return patterns


application = ProtocolTypeRouter({
    "http": http_app,
    "websocket": URLRouter(_websocket_urlpatterns()),
})
