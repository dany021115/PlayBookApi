from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class Bookmaker(TimeStamped):
    slug = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=80)
    country = models.CharField(max_length=80, blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
