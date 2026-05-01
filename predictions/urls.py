from django.urls import path

from predictions.api.v1.endpoints.views import (
    AccuracyView,
    PredictionDetailView,
    PredictionListView,
    StrategyListView,
)

app_name = "predictions"

urlpatterns = [
    path("strategies/", StrategyListView.as_view(), name="strategy-list"),
    path("predictions/accuracy/", AccuracyView.as_view(), name="prediction-accuracy"),
    path("predictions/", PredictionListView.as_view(), name="prediction-list"),
    path("predictions/<int:pk>/", PredictionDetailView.as_view(), name="prediction-detail"),
]
