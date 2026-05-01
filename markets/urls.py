from django.urls import path

from markets.api.v1.endpoints.views import (
    BookmakerListView,
    LiveMatchListView,
    MatchDetailView,
    MatchListView,
    OddsByEventView,
    OddsBySportView,
    SportListView,
)

app_name = "markets"

urlpatterns = [
    path("sports/", SportListView.as_view(), name="sport-list"),
    path("bookmakers/", BookmakerListView.as_view(), name="bookmaker-list"),
    path("matches/live/", LiveMatchListView.as_view(), name="match-live"),
    path("matches/", MatchListView.as_view(), name="match-list"),
    path("matches/<int:pk>/", MatchDetailView.as_view(), name="match-detail"),
    path("odds/<str:sport>/", OddsBySportView.as_view(), name="odds-by-sport"),
    path("odds/event/<int:event_id>/", OddsByEventView.as_view(), name="odds-by-event"),
]
