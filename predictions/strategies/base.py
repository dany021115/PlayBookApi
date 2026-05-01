from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Pick:
    market: str            # "h2h", "totals", "spreads"
    outcome: str           # "home" / "away" / "draw" / "over" / "under"
    line: Decimal | None   # totals/spreads line (None for h2h)
    bookmaker_id: int      # markets.Bookmaker pk
    price: Decimal         # decimal odds
    confidence: int        # 0-100


class BasePickStrategy(ABC):
    """Strategies are pure functions of (event, features) → Pick or None."""

    name: str = ""

    def __init__(self, params: dict | None = None) -> None:
        self.params = params or {}

    @abstractmethod
    def run(self, event, features: dict) -> Pick | None:
        """Return a Pick or None if no opportunity is found."""
