from django.conf import settings
from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class NotificationLog(TimeStamped):
    class Kind(models.TextChoices):
        NEW_PREDICTION = "new_prediction", "New Prediction"
        PREDICTION_SETTLED = "prediction_settled", "Prediction Settled"
        MATCH_STARTING = "match_starting", "Match Starting"
        OTHER = "other", "Other"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="notification_logs")
    kind = models.CharField(max_length=32, choices=Kind.choices)
    title = models.CharField(max_length=160, blank=True, default="")
    body = models.TextField(blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=False)
    error = models.TextField(blank=True, default="")
    fcm_message_id = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["kind", "-created_at"]),
        ]
        ordering = ["-created_at"]
