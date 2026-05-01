from django.urls import path

from follows.api.v1.endpoints.views import (
    FollowedLeagueDestroy,
    FollowedLeagueListCreate,
    FollowedSportDestroy,
    FollowedSportListCreate,
    FollowedStrategyDestroy,
    FollowedStrategyListCreate,
    SavedPredictionDestroy,
    SavedPredictionListCreate,
)

app_name = "follows"

urlpatterns = [
    path("me/follows/sports/", FollowedSportListCreate.as_view(), name="sport-follow-list"),
    path("me/follows/sports/<int:pk>/", FollowedSportDestroy.as_view(), name="sport-follow-delete"),
    path("me/follows/leagues/", FollowedLeagueListCreate.as_view(), name="league-follow-list"),
    path("me/follows/leagues/<int:pk>/", FollowedLeagueDestroy.as_view(), name="league-follow-delete"),
    path("me/follows/strategies/", FollowedStrategyListCreate.as_view(), name="strategy-follow-list"),
    path("me/follows/strategies/<int:pk>/", FollowedStrategyDestroy.as_view(), name="strategy-follow-delete"),
    path("me/saved-predictions/", SavedPredictionListCreate.as_view(), name="saved-list"),
    path("me/saved-predictions/<int:pk>/", SavedPredictionDestroy.as_view(), name="saved-delete"),
]
