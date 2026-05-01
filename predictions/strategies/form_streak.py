"""Pick `home win` (h2h) when home team has a winning streak in last 5 games."""

from __future__ import annotations

from decimal import Decimal

from predictions.strategies.base import BasePickStrategy, Pick


class FormStreakStrategy(BasePickStrategy):
    name = "form_streak"

    def run(self, event, features: dict) -> Pick | None:
        min_wins = int(self.params.get("min_wins", 4))
        min_price = float(self.params.get("min_price", 1.7))

        form = features.get("form") or {}
        home_form = form.get("home") or []
        away_form = form.get("away") or []

        market_data: dict = features.get("market_odds") or {}
        h2h = market_data.get("h2h") or []

        def _best_for(outcome: str):
            for entry in h2h:
                if entry["outcome"] == outcome and entry.get("snapshots"):
                    return max(entry["snapshots"], key=lambda s: float(s.get("price", 0)))
            return None

        # Home streak
        if home_form.count("W") >= min_wins:
            best = _best_for("home")
            if best and float(best["price"]) >= min_price:
                return Pick(
                    market="h2h", outcome="home", line=None,
                    bookmaker_id=int(best["bookmaker_id"]),
                    price=Decimal(str(best["price"])),
                    confidence=min(95, 60 + (home_form.count("W") - min_wins) * 5),
                )
        # Away streak
        if away_form.count("W") >= min_wins:
            best = _best_for("away")
            if best and float(best["price"]) >= min_price:
                return Pick(
                    market="h2h", outcome="away", line=None,
                    bookmaker_id=int(best["bookmaker_id"]),
                    price=Decimal(str(best["price"])),
                    confidence=min(95, 60 + (away_form.count("W") - min_wins) * 5),
                )
        return None
