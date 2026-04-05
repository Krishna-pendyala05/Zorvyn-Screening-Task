from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Domain: users | Purpose: Admin interface configuration for user management


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Facilitates RBAC administration natively using Django's baseline user architecture
    model = User
    list_display = ("id", "username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("RBAC Permissions", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("RBAC Permissions", {"fields": ("role",)}),
    )
    ordering = ("username",)

    def log_addition(self, request, object, message):
        super().log_addition(request, object, message)
        # _audit_log_created guards against save_model and log_addition both firing a CREATE log
        if not getattr(object, "_audit_log_created", False):
            from common.utils import record_audit_log
            from common.models import AuditLog
            record_audit_log(
                user=request.user,
                instance=object,
                action=AuditLog.Action.CREATE,
                changes={
                    "username": object.username,
                    "email": object.email,
                    "role": object.role,
                    "is_active": str(object.is_active),
                },
            )
            object._audit_log_created = True

    def save_model(self, request, obj, form, change):
        from common.utils import record_audit_log, compute_delta
        from common.models import AuditLog

        if not change:
            super().save_model(request, obj, form, change)
            if not getattr(obj, "_audit_log_created", False):
                record_audit_log(
                    user=request.user,
                    instance=obj,
                    action=AuditLog.Action.CREATE,
                    changes={
                        "username": obj.username,
                        "email": obj.email,
                        "role": obj.role,
                        "is_active": str(obj.is_active),
                    },
                )
                obj._audit_log_created = True
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
            changes = compute_delta(old_data, new_data)
            if changes:
                record_audit_log(
                    user=request.user,
                    instance=obj,
                    action=AuditLog.Action.UPDATE,
                    changes=changes,
                )

    def delete_model(self, request, obj):
        from common.utils import record_audit_log
        from common.models import AuditLog

        record_audit_log(
            user=request.user,
            instance=obj,
            action=AuditLog.Action.DELETE,
            changes={"id": str(obj.id), "username": obj.username, "status": "Hard Deleted via Admin"},
        )
        super().delete_model(request, obj)
