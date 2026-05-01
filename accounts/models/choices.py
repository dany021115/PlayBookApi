from django.db import models


class ProviderAuthChoices(models.TextChoices):
    PASSWORD = "password", "Password"
    GOOGLE = "google", "Google"
    APPLE = "apple", "Apple"


class PlatformChoices(models.TextChoices):
    UNKNOWN = "unknown", "Unknown"
    ANDROID = "ANDROID", "Android"
    IOS = "IOS", "iOS"
    WEB = "WEB", "Web"
