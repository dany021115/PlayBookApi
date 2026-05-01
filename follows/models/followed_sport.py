from django.conf import settings
from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class FollowedSport(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="followed_sports")
    sport = models.ForeignKey("markets.Sport", on_delete=models.CASCADE,
                              related_name="followers")

    class Meta:
        unique_together = ("user", "sport")
        ordering = ["-created_at"]
