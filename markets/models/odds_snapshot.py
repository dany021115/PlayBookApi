from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class OddsSnapshot(TimeStamped):
    class Market(models.TextChoices):
        H2H = "h2h", "Head-to-Head"
        SPREADS = "spreads", "Spreads"
        TOTALS = "totals", "Totals"
        BTTS = "btts", "Both Teams To Score"
        DOUBLE_CHANCE = "double_chance", "Double Chance"

    upstream_id = models.IntegerField(unique=True, db_index=True,
                                      help_text="OddsSnapshot id from sports-odds-api.")
    event = models.ForeignKey("markets.Event", on_delete=models.CASCADE, related_name="odds")
    bookmaker = models.ForeignKey("markets.Bookmaker", on_delete=models.CASCADE, related_name="snapshots")
    market = models.CharField(max_length=24, choices=Market.choices)
    outcome = models.CharField(max_length=40)
    line = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=3)
    captured_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["event", "captured_at"]),
            models.Index(fields=["event", "bookmaker", "market"]),
        ]
        ordering = ["-captured_at"]

    def __str__(self) -> str:
        return f"{self.bookmaker} {self.market}/{self.outcome} @ {self.price}"
