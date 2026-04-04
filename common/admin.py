from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "model_name", "user", "timestamp")
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("object_id", "user__username", "model_name")
    readonly_fields = ("id", "user", "model_name", "object_id", "action", "changes", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
