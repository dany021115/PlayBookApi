from django.contrib import admin
from unfold.admin import ModelAdmin

from compliance.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ("created_at", "user", "method", "path", "status_code", "duration_ms", "ip_address")
    list_filter = ("method", "status_code")
    search_fields = ("path", "user__email", "ip_address")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
