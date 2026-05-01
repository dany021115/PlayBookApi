from django.conf import settings
from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class SavedPrediction(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="saved_predictions")
    prediction = models.ForeignKey("predictions.Prediction", on_delete=models.CASCADE,
                                   related_name="savers")

    class Meta:
        unique_together = ("user", "prediction")
        ordering = ["-created_at"]
