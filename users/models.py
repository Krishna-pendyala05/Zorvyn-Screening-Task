from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

# Domain: users | Purpose: Custom User model with role field for RBAC


class User(AbstractUser):
    # Extends Django baseline to secure system endpoints using role-based tiering

    class UserRole(models.TextChoices):
        VIEWER = "VIEWER", "Viewer"
        ANALYST = "ANALYST", "Analyst"
        ADMIN = "ADMIN", "Admin"

    # UUIDs prevent sequential ID enumeration on user accounts
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.VIEWER,
    )

    # is_active is the soft-delete mechanism for users
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.role})"
