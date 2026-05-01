from django.contrib import admin
from unfold.admin import ModelAdmin

from notifications.models import DeviceToken, NotificationLog


@admin.register(DeviceToken)
class DeviceTokenAdmin(ModelAdmin):
    list_display = ("user", "platform", "active", "last_seen_at")
    list_filter = ("platform", "active")
    search_fields = ("user__email", "token")
    readonly_fields = ("created_at", "updated_at", "last_seen_at")


@admin.register(NotificationLog)
class NotificationLogAdmin(ModelAdmin):
    list_display = ("created_at", "user", "kind", "title", "success", "fcm_message_id")
    list_filter = ("kind", "success")
    search_fields = ("user__email", "title", "body")
    date_hierarchy = "created_at"
    readonly_fields = [
        "user", "kind", "title", "body", "payload",
        "success", "error", "fcm_message_id", "created_at", "updated_at",
    ]
