from .models import AuditLog

def record_audit_log(user, instance, action, changes=None):
    """
    Utility to create an AuditLog entry.
    Handles both authenticated Users and AnonymousUser instances.
    """
    if changes is None:
        changes = {}
    
    # Ensure AnonymousUser is stored as None (null in DB)
    audit_user = user if user.is_authenticated else None
    
    AuditLog.objects.create(
        user=audit_user,
        model_name=instance.__class__.__name__,
        object_id=instance.id,
        action=action,
        changes=changes
    )
