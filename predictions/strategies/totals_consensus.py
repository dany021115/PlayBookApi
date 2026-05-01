"""Pick over/under at line 2.5 based on team scoring averages."""

from __future__ import annotations

from decimal import Decimal

from predictions.strategies.base import BasePickStrategy, Pick


class TotalsConsensusStrategy(BasePickStrategy):
    name = "totals_consensus"

    def run(self, event, features: dict) -> Pick | None:
        over_thr = float(self.params.get("over_threshold", 2.8))
        under_thr = float(self.params.get("under_threshold", 2.0))
        target_line = float(self.params.get("line", 2.5))

        avg = features.get("avg_goals") or {}
        avg_total = (avg.get("home") or 0) + (avg.get("away") or 0)

        market_data: dict = features.get("market_odds") or {}
        totals = market_data.get("totals") or []

        def _best_for(outcome: str, line_val: float):
            for entry in totals:
                if entry["outcome"] == outcome and float(entry.get("line") or 0) == line_val:
                    if entry.get("snapshots"):
                        return max(entry["snapshots"], key=lambda s: float(s.get("price", 0)))
            return None

        if avg_total >= over_thr:
            best = _best_for("over", target_line)
            if best:
                return Pick(
                    market="totals", outcome="over",
                    line=Decimal(str(target_line)),
                    bookmaker_id=int(best["bookmaker_id"]),
                    price=Decimal(str(best["price"])),
                    confidence=min(90, 50 + int((avg_total - over_thr) * 20)),
                )
        if avg_total > 0 and avg_total <= under_thr:
            best = _best_for("under", target_line)
            if best:
                return Pick(
                    market="totals", outcome="under",
                    line=Decimal(str(target_line)),
                    bookmaker_id=int(best["bookmaker_id"]),
                    price=Decimal(str(best["price"])),
                    confidence=min(90, 50 + int((under_thr - avg_total) * 30)),
                )
        return None
