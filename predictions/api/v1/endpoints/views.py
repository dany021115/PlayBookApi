from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from predictions.api.v1.serializers import PredictionSerializer, StrategySerializer
from predictions.models import Prediction, Strategy


class StrategyListView(generics.ListAPIView):
    serializer_class = StrategySerializer
    queryset = Strategy.objects.filter(enabled=True)
    pagination_class = None
    permission_classes = [IsAuthenticated, HasAPIKey]


class PredictionListView(generics.ListAPIView):
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated, HasAPIKey]
    filterset_fields = ["status", "result", "strategy", "market"]

    def get_queryset(self):
        qs = Prediction.objects.select_related(
            "event__league__sport", "event__home_team", "event__away_team",
            "strategy", "recommended_bookmaker",
        )
        sport = self.request.query_params.get("sport")
        if sport:
            qs = qs.filter(event__league__sport__key__iexact=sport)
        league = self.request.query_params.get("league")
        if league:
            qs = qs.filter(event__league__slug=league)
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        strategy = self.request.query_params.get("strategy")
        if strategy:
            qs = qs.filter(strategy__name=strategy)
        return qs.order_by("-created_at")


class PredictionDetailView(generics.RetrieveAPIView):
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated, HasAPIKey]
    queryset = Prediction.objects.select_related(
        "event__league__sport", "event__home_team", "event__away_team",
        "strategy", "recommended_bookmaker",
    )


class AccuracyView(generics.GenericAPIView):
    """GET /api/v1/predictions/accuracy/?strategy=<name|all>

    Returns hit rate + ROI per strategy across all settled predictions.
    """

    permission_classes = [IsAuthenticated, HasAPIKey]

    def get(self, request):
        from decimal import Decimal

        strategy_filter = request.query_params.get("strategy")
        qs = Prediction.objects.filter(status=Prediction.Status.SETTLED)
        if strategy_filter and strategy_filter != "all":
            qs = qs.filter(strategy__name=strategy_filter)

        per_strategy: dict[str, dict] = {}
        for p in qs.select_related("strategy"):
            agg = per_strategy.setdefault(p.strategy.name, {
                "won": 0, "lost": 0, "push": 0, "void": 0, "stake": Decimal(0), "pnl": Decimal(0),
            })
            agg[p.result] = agg.get(p.result, 0) + 1
            agg["stake"] += Decimal("1")
            if p.result == Prediction.Result.WON:
                agg["pnl"] += Decimal(p.recommended_price) - Decimal("1")
            elif p.result == Prediction.Result.LOST:
                agg["pnl"] -= Decimal("1")

        out = []
        for name, agg in per_strategy.items():
            won, lost, push, void = agg.get("won", 0), agg.get("lost", 0), agg.get("push", 0), agg.get("void", 0)
            decided = won + lost
            hit_rate = round(won / decided * 100, 1) if decided else 0.0
            roi = round(float(agg["pnl"]) / float(agg["stake"]) * 100, 1) if agg["stake"] else 0.0
            out.append({
                "strategy": name,
                "settled": won + lost + push + void,
                "won": won,
                "lost": lost,
                "push": push,
                "void": void,
                "hit_rate_pct": hit_rate,
                "roi_pct": roi,
            })
        return Response({"results": out})
