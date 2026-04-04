from django.db import models
from django.conf import settings
import uuid

# Domain: common | Purpose: Centralized audit logging for the entire project

class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who performed the action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs"
    )
    
    # What was affected
    model_name = models.CharField(max_length=100)
    object_id = models.UUIDField(null=True)
    
    # What action was taken
    action = models.CharField(max_length=10, choices=Action.choices)
    
    # What changed (JSON delta)
    changes = models.JSONField(default=dict, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} on {self.model_name} at {self.timestamp}"
