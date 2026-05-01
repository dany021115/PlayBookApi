from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class Sport(TimeStamped):
    key = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
