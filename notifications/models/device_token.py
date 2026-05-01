from django.conf import settings
from django.db import models

from PlayBookApi.utils.models.timestamped import TimeStamped


class DeviceToken(TimeStamped):
    class Platform(models.TextChoices):
        IOS = "ios", "iOS"
        ANDROID = "android", "Android"
        WEB = "web", "Web"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="device_tokens")
    token = models.CharField(max_length=512, unique=True)
    platform = models.CharField(max_length=12, choices=Platform.choices, default=Platform.ANDROID)
    active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_seen_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.platform}:{self.token[:12]}…"
