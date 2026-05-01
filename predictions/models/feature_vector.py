from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class FeatureVector(TimeStamped):
    """Snapshot of features used to generate predictions for an Event.

    Capturing this lets us trace 'what we knew at the time' for any Prediction.
    """

    event = models.ForeignKey(
        "markets.Event", on_delete=models.CASCADE, related_name="feature_vectors",
    )
    captured_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(default=dict)

    class Meta:
        ordering = ["-captured_at"]
        indexes = [models.Index(fields=["event", "-captured_at"])]

    def __str__(self) -> str:
        return f"FeatureVector<event={self.event_id}>"
