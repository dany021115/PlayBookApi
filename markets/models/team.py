from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class Team(TimeStamped):
    league = models.ForeignKey("markets.League", on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180)
    logo_url = models.URLField(blank=True, default="")

    class Meta:
        unique_together = ("league", "slug")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
