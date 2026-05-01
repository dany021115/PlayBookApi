from django.contrib import admin
from unfold.admin import ModelAdmin

from follows.models import (
    FollowedLeague,
    FollowedSport,
    FollowedStrategy,
    SavedPrediction,
)


@admin.register(FollowedSport)
class FollowedSportAdmin(ModelAdmin):
    list_display = ("user", "sport", "created_at")
    search_fields = ("user__email", "sport__key")


@admin.register(FollowedLeague)
class FollowedLeagueAdmin(ModelAdmin):
    list_display = ("user", "league", "created_at")
    search_fields = ("user__email", "league__name")


@admin.register(FollowedStrategy)
class FollowedStrategyAdmin(ModelAdmin):
    list_display = ("user", "strategy", "created_at")
    search_fields = ("user__email", "strategy__name")


@admin.register(SavedPrediction)
class SavedPredictionAdmin(ModelAdmin):
    list_display = ("user", "prediction", "created_at")
    search_fields = ("user__email",)
