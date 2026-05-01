"""Value-bet detector: pick the highest-priced outcome that beats consensus by `min_edge`."""

from __future__ import annotations

from decimal import Decimal

from predictions.strategies.base import BasePickStrategy, Pick


class ValueBetStrategy(BasePickStrategy):
    name = "value_bet"

    def run(self, event, features: dict) -> Pick | None:
        min_edge = float(self.params.get("min_edge", 0.05))
        market_data: dict = features.get("market_odds") or {}

        best_pick: Pick | None = None
        best_edge = -1.0  # so first candidate satisfying min_edge always wins

        for market, outcomes in market_data.items():
            # outcomes: list of dicts {outcome, line, snapshots: [{price, bookmaker_id}, ...]}
            for entry in outcomes:
                snapshots = entry.get("snapshots") or []
                if len(snapshots) < 1:
                    continue
                prices = [float(s["price"]) for s in snapshots if s.get("price")]
                if not prices:
                    continue
                consensus_implied = sum(1 / p for p in prices) / len(prices)
                # consensus_implied already includes margin; we don't strip it for MVP
                best = max(snapshots, key=lambda s: float(s.get("price", 0)))
                best_price = float(best["price"])
                edge = best_price * consensus_implied - 1
                if edge < min_edge:
                    continue
                if edge > best_edge:
                    best_edge = edge
                    best_pick = Pick(
                        market=market,
                        outcome=entry["outcome"],
                        line=Decimal(str(entry["line"])) if entry.get("line") is not None else None,
                        bookmaker_id=int(best["bookmaker_id"]),
                        price=Decimal(str(best_price)),
                        confidence=min(95, int(50 + edge * 500)),
                    )
        return best_pick
