from django.conf import settings
from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class FollowedStrategy(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="followed_strategies")
    strategy = models.ForeignKey("predictions.Strategy", on_delete=models.CASCADE,
                                 related_name="followers")

    class Meta:
        unique_together = ("user", "strategy")
        ordering = ["-created_at"]
