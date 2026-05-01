from django.conf import settings
from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class FollowedLeague(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="followed_leagues")
    league = models.ForeignKey("markets.League", on_delete=models.CASCADE,
                               related_name="followers")

    class Meta:
        unique_together = ("user", "league")
        ordering = ["-created_at"]
