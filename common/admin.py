from django.contrib import admin
from .models import AuditLog

# Domain: common | Purpose: Read-only admin interface for forensic audit log review


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # Enforces absolute immutability upon the forensic logs while providing visual oversight
    list_display = ("action", "model_name", "user", "timestamp")
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("object_id", "user__username", "model_name")
    readonly_fields = ("id", "user", "model_name", "object_id", "action", "changes", "timestamp")

    # Audit logs must be immutable; deny all write operations from the admin UI
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
