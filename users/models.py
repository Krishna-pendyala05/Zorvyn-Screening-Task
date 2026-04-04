from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

# Domain: users | Purpose: Custom User model with Role-Based Access Control fields

class User(AbstractUser):
    class UserRole(models.TextChoices):
        VIEWER = "VIEWER", "Viewer"
        ANALYST = "ANALYST", "Analyst"
        ADMIN = "ADMIN", "Admin"

    # UUID as primary key is required for all models in this project
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Custom role field for RBAC
    role = models.CharField(
        max_length=10, 
        choices=UserRole.choices, 
        default=UserRole.VIEWER,
        help_text="Role-based access level for this user."
    )
    
    # Standard is_active status - used by IsActiveUser permission gate
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active."
    )

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.role})"
