from django.db import models
from django.conf import settings
import uuid

# Domain: common | Purpose: Centralized audit log for all write operations across the system


class AuditLog(models.Model):
    # Centralizes forensic tracking of system-wide state changes and data tampering
    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # SET_NULL preserves the log entry if the acting user is later deactivated
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )

    model_name = models.CharField(max_length=100)
    object_id = models.UUIDField(null=True)
    action = models.CharField(max_length=10, choices=Action.choices)

    # JSON delta stores only the changed fields, not a full object snapshot
    changes = models.JSONField(default=dict, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} on {self.model_name} at {self.timestamp}"
