from rest_framework import serializers

from predictions.models import Prediction, Strategy


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ["id", "name", "type", "enabled", "description"]


class PredictionSerializer(serializers.ModelSerializer):
    strategy = serializers.CharField(source="strategy.name", read_only=True)
    strategy_type = serializers.CharField(source="strategy.type", read_only=True)
    bookmaker = serializers.CharField(source="recommended_bookmaker.slug", read_only=True)
    sport = serializers.CharField(source="event.league.sport.key", read_only=True)
    league = serializers.CharField(source="event.league.name", read_only=True)
    home_team = serializers.CharField(source="event.home_team.name", read_only=True)
    away_team = serializers.CharField(source="event.away_team.name", read_only=True)
    start_time = serializers.DateTimeField(source="event.start_time", read_only=True)

    class Meta:
        model = Prediction
        fields = [
            "id", "event_id", "sport", "league", "home_team", "away_team", "start_time",
            "strategy", "strategy_type",
            "market", "outcome", "line",
            "bookmaker", "recommended_price",
            "confidence", "reasoning", "reasoning_lang",
            "status", "result", "settled_at", "created_at",
        ]
