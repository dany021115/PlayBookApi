from rest_framework import serializers

from markets.models import Bookmaker, Event, League, OddsSnapshot, Sport, Team


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ["id", "key", "name", "slug"]


class LeagueSerializer(serializers.ModelSerializer):
    sport = serializers.CharField(source="sport.key", read_only=True)

    class Meta:
        model = League
        fields = ["id", "name", "country", "slug", "sport"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "slug", "logo_url"]


class BookmakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmaker
        fields = ["id", "slug", "name", "country"]


class EventListSerializer(serializers.ModelSerializer):
    sport = serializers.CharField(source="league.sport.key", read_only=True)
    league = serializers.CharField(source="league.name", read_only=True)
    home_team = serializers.CharField(source="home_team.name", read_only=True)
    away_team = serializers.CharField(source="away_team.name", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "upstream_id", "sport", "league",
            "home_team", "away_team", "status", "start_time",
            "home_score", "away_score", "minute", "updated_at",
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    sport = serializers.CharField(source="league.sport.key", read_only=True)
    league = LeagueSerializer(read_only=True)
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "upstream_id", "sport", "league",
            "home_team", "away_team", "status", "start_time",
            "home_score", "away_score", "minute", "updated_at",
        ]


class OddsSnapshotSerializer(serializers.ModelSerializer):
    bookmaker = serializers.CharField(source="bookmaker.slug", read_only=True)
    sport = serializers.CharField(source="event.league.sport.key", read_only=True)
    home_team = serializers.CharField(source="event.home_team.name", read_only=True)
    away_team = serializers.CharField(source="event.away_team.name", read_only=True)
    start_time = serializers.DateTimeField(source="event.start_time", read_only=True)

    class Meta:
        model = OddsSnapshot
        fields = [
            "id", "event_id", "sport", "home_team", "away_team", "start_time",
            "bookmaker", "market", "outcome", "line", "price", "captured_at",
        ]
