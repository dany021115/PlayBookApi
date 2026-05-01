from django.contrib import admin
from unfold.admin import ModelAdmin

from accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ("user", "provider", "country", "phone", "created_at")
    list_filter = ("provider", "country")
    search_fields = ("user__email", "user__username", "phone")
    readonly_fields = ("created_at", "updated_at")
