from .models import AuditLog

# Domain: common | Purpose: Shared utilities for audit logging across all domain apps


def compute_delta(old_data: dict, new_data: dict) -> dict:
    # Returns only changed fields to keep audit logs minimal and readable
    return {
        field: [old_data[field], new_data[field]]
        for field in old_data
        if old_data[field] != new_data[field]
    }


def record_audit_log(user, instance, action, changes=None):
    if changes is None:
        changes = {}

    # AnonymousUser cannot be stored as a FK; coerce to None
    audit_user = user if user.is_authenticated else None

    AuditLog.objects.create(
        user=audit_user,
        model_name=instance.__class__.__name__,
        object_id=instance.id,
        action=action,
        changes=changes,
    )
