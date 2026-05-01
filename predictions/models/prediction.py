from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class Prediction(TimeStamped):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SETTLED = "settled", "Settled"
        VOIDED = "voided", "Voided"

    class Result(models.TextChoices):
        WON = "won", "Won"
        LOST = "lost", "Lost"
        PUSH = "push", "Push"
        VOID = "void", "Void"

    event = models.ForeignKey(
        "markets.Event", on_delete=models.CASCADE, related_name="predictions",
    )
    strategy = models.ForeignKey(
        "predictions.Strategy", on_delete=models.PROTECT, related_name="predictions",
    )
    feature_vector = models.ForeignKey(
        "predictions.FeatureVector", on_delete=models.SET_NULL, null=True, blank=True,
    )

    market = models.CharField(max_length=24)
    outcome = models.CharField(max_length=40)
    line = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    recommended_bookmaker = models.ForeignKey(
        "markets.Bookmaker", on_delete=models.PROTECT, related_name="predictions",
    )
    recommended_price = models.DecimalField(max_digits=8, decimal_places=3)

    confidence = models.PositiveSmallIntegerField()
    reasoning = models.TextField(blank=True, default="")
    reasoning_lang = models.CharField(max_length=8, default="es")

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING,
    )
    result = models.CharField(max_length=16, choices=Result.choices, blank=True, default="")
    settled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["event", "strategy"]),
            models.Index(fields=["result", "-settled_at"]),
        ]
        unique_together = [("event", "strategy", "market", "outcome")]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return (
            f"Prediction<{self.strategy.name} {self.market}/{self.outcome} "
            f"@ {self.recommended_price} ({self.status})>"
        )
