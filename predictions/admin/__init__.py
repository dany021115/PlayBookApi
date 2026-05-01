from django.contrib import admin
from unfold.admin import ModelAdmin

from predictions.models import FeatureVector, Prediction, Strategy


@admin.register(Strategy)
class StrategyAdmin(ModelAdmin):
    list_display = ("name", "type", "enabled", "updated_at")
    list_filter = ("type", "enabled")
    search_fields = ("name", "description")


@admin.register(Prediction)
class PredictionAdmin(ModelAdmin):
    list_display = (
        "event", "strategy", "market", "outcome", "line",
        "recommended_bookmaker", "recommended_price", "confidence",
        "status", "result", "settled_at",
    )
    list_filter = ("status", "result", "strategy", "market")
    search_fields = (
        "event__home_team__name", "event__away_team__name", "reasoning",
    )
    readonly_fields = ("created_at", "updated_at", "settled_at")
    date_hierarchy = "created_at"
    autocomplete_fields = ("event", "strategy", "feature_vector", "recommended_bookmaker")
    list_per_page = 100


@admin.register(FeatureVector)
class FeatureVectorAdmin(ModelAdmin):
    list_display = ("event", "captured_at")
    date_hierarchy = "captured_at"
    search_fields = ("event__home_team__name", "event__away_team__name")
    autocomplete_fields = ("event",)
