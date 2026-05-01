from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from accounts.models.choices import ProviderAuthChoices
from PlayBookApi.utils.models.timestamped import TimeStamped


def _avatar_upload_to(instance, filename):
    return f"avatars/{instance.user_id}/{filename}"


class Profile(TimeStamped):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(upload_to=_avatar_upload_to, blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, default="")
    provider = models.CharField(
        max_length=20,
        choices=ProviderAuthChoices.choices,
        blank=True,
        null=True,
    )
    locale = models.CharField(max_length=8, blank=True, default="es")
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Profile<{self.user_id} {self.user.email}>"
