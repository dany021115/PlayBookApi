from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class League(TimeStamped):
    sport = models.ForeignKey("markets.Sport", on_delete=models.CASCADE, related_name="leagues")
    name = models.CharField(max_length=160)
    country = models.CharField(max_length=80, blank=True, default="")
    slug = models.SlugField(max_length=180)

    class Meta:
        unique_together = ("sport", "slug")
        ordering = ["country", "name"]

    def __str__(self) -> str:
        return f"{self.sport.key}:{self.name}"
