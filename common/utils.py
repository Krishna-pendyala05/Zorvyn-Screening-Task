from .models import AuditLog

def record_audit_log(user, instance, action, changes=None):
    """
    Utility to create an AuditLog entry.
    """
    if changes is None:
        changes = {}
    
    AuditLog.objects.create(
        user=user,
        model_name=instance.__class__.__name__,
        object_id=instance.id,
        action=action,
        changes=changes
    )
