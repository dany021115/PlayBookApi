from rest_framework import serializers

from follows.models import FollowedLeague, FollowedSport, FollowedStrategy, SavedPrediction


class FollowedSportSerializer(serializers.ModelSerializer):
    sport_key = serializers.CharField(source="sport.key", read_only=True)
    sport_name = serializers.CharField(source="sport.name", read_only=True)

    class Meta:
        model = FollowedSport
        fields = ["id", "sport", "sport_key", "sport_name", "created_at"]


class FollowedLeagueSerializer(serializers.ModelSerializer):
    league_name = serializers.CharField(source="league.name", read_only=True)
    sport = serializers.CharField(source="league.sport.key", read_only=True)

    class Meta:
        model = FollowedLeague
        fields = ["id", "league", "league_name", "sport", "created_at"]


class FollowedStrategySerializer(serializers.ModelSerializer):
    strategy_name = serializers.CharField(source="strategy.name", read_only=True)

    class Meta:
        model = FollowedStrategy
        fields = ["id", "strategy", "strategy_name", "created_at"]


class SavedPredictionSerializer(serializers.ModelSerializer):
    home_team = serializers.CharField(source="prediction.event.home_team.name", read_only=True)
    away_team = serializers.CharField(source="prediction.event.away_team.name", read_only=True)
    market = serializers.CharField(source="prediction.market", read_only=True)
    outcome = serializers.CharField(source="prediction.outcome", read_only=True)
    price = serializers.DecimalField(source="prediction.recommended_price", max_digits=8, decimal_places=3, read_only=True)
    status = serializers.CharField(source="prediction.status", read_only=True)
    result = serializers.CharField(source="prediction.result", read_only=True)

    class Meta:
        model = SavedPrediction
        fields = ["id", "prediction", "home_team", "away_team",
                  "market", "outcome", "price", "status", "result", "created_at"]
