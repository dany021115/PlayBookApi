from django.contrib import admin
from unfold.admin import ModelAdmin

from markets.models import Bookmaker, Event, League, OddsSnapshot, Sport, Team


@admin.register(Sport)
class SportAdmin(ModelAdmin):
    list_display = ("name", "key", "slug")
    search_fields = ("name", "key", "slug")


@admin.register(League)
class LeagueAdmin(ModelAdmin):
    list_display = ("name", "sport", "country")
    list_filter = ("sport", "country")
    search_fields = ("name", "slug")


@admin.register(Team)
class TeamAdmin(ModelAdmin):
    list_display = ("name", "league")
    list_filter = ("league__sport",)
    search_fields = ("name", "slug")


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ("home_team", "away_team", "status", "start_time",
                    "home_score", "away_score", "minute", "upstream_id")
    list_filter = ("status", "league__sport")
    search_fields = ("home_team__name", "away_team__name", "league__name")
    date_hierarchy = "start_time"
    readonly_fields = ("upstream_id", "upstream_updated_at", "created_at", "updated_at")
    list_per_page = 100


@admin.register(Bookmaker)
class BookmakerAdmin(ModelAdmin):
    list_display = ("name", "slug", "country")
    search_fields = ("name", "slug")


@admin.register(OddsSnapshot)
class OddsSnapshotAdmin(ModelAdmin):
    list_display = ("event", "bookmaker", "market", "outcome", "line", "price", "captured_at")
    list_filter = ("market", "bookmaker")
    date_hierarchy = "captured_at"
    search_fields = (
        "event__home_team__name", "event__away_team__name", "bookmaker__name",
    )
    readonly_fields = ("upstream_id", "created_at", "updated_at")
