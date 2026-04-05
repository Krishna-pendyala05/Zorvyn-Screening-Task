from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer
from .permissions import IsActiveUser, IsAdminRole
from common.utils import record_audit_log, compute_delta
from common.models import AuditLog

# Domain: users | Purpose: Admin-only endpoints for user account management


@extend_schema(tags=["Users"])
class UserListCreateView(generics.ListCreateAPIView):
    # Bulk management view enabling admins to rapidly audit or provision active directories
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser, IsAdminRole]

    def perform_create(self, serializer):
        instance = serializer.save()
        record_audit_log(
            user=self.request.user,
            instance=instance,
            action=AuditLog.Action.CREATE,
            changes={
                "username": instance.username,
                "email": instance.email,
                "role": instance.role,
                "is_active": str(instance.is_active),
            },
        )


@extend_schema(tags=["Users"])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Isolates structural role upgrades and soft-terminations for individual accounts
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser, IsAdminRole]

    def perform_update(self, serializer):
        old = self.get_object()
        old_data = {
            "username": old.username,
            "email": old.email,
            "role": old.role,
            "is_active": str(old.is_active),
        }
        instance = serializer.save()
        new_data = {
            "username": instance.username,
            "email": instance.email,
            "role": instance.role,
            "is_active": str(instance.is_active),
        }
        changes = compute_delta(old_data, new_data)
        if changes:
            record_audit_log(
                user=self.request.user,
                instance=instance,
                action=AuditLog.Action.UPDATE,
                changes=changes,
            )

    def perform_destroy(self, instance):
        # Soft-delete preserves the user record for forensic accountability
        instance.is_active = False
        instance.save()
        record_audit_log(
            user=self.request.user,
            instance=instance,
            action=AuditLog.Action.DELETE,
            changes={"id": str(instance.id), "username": instance.username, "status": "Deactivated"},
        )
