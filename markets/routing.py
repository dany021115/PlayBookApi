from django.urls import path

from markets.consumers import MatchStreamConsumer

websocket_urlpatterns = [
    path("ws/matches/", MatchStreamConsumer.as_asgi()),
]
