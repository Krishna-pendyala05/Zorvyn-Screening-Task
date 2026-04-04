from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Domain: users | Purpose: Admin interface configuration for User management

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Customized Admin interface for the Zorvyn User model.
    """
    model = User
    # Display these columns in the list view
    list_display = ("id", "username", "email", "role", "is_active", "is_staff")
    # Quick filters on the sidebar
    list_filter = ("role", "is_active", "is_staff")
    
    # Define fields for the edit form
    fieldsets = UserAdmin.fieldsets + (
        ("RBAC Permissions", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("RBAC Permissions", {"fields": ("role",)}),
    )
    ordering = ("username",)

    def save_model(self, request, obj, form, change):
        from common.utils import record_audit_log
        from common.models import AuditLog

        if not change:
            super().save_model(request, obj, form, change)
            changes = {
                "username": obj.username,
                "email": obj.email,
                "role": obj.role,
                "is_active": str(obj.is_active),
            }
            record_audit_log(user=request.user, instance=obj, action=AuditLog.Action.CREATE, changes=changes)
        else:
            old_obj = User.objects.get(pk=obj.pk)
            old_data = {
                "username": old_obj.username,
                "email": old_obj.email,
                "role": old_obj.role,
                "is_active": str(old_obj.is_active),
            }
            super().save_model(request, obj, form, change)
            new_data = {
                "username": obj.username,
                "email": obj.email,
                "role": obj.role,
                "is_active": str(obj.is_active),
            }
            changes = {
                field: [old_data[field], new_data[field]]
                for field in old_data
                if old_data[field] != new_data[field]
            }
            if changes:
                record_audit_log(user=request.user, instance=obj, action=AuditLog.Action.UPDATE, changes=changes)

    def delete_model(self, request, obj):
        from common.utils import record_audit_log
        from common.models import AuditLog
        
        record_audit_log(
            user=request.user,
            instance=obj,
            action=AuditLog.Action.DELETE,
            changes={"id": str(obj.id), "username": obj.username, "status": "Hard Deleted via Admin"}
        )
        super().delete_model(request, obj)
