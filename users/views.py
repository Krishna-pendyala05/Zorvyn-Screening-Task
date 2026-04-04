from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer
from .permissions import IsActiveUser, IsAdminRole
from common.utils import record_audit_log
from common.models import AuditLog

# Domain: users | Purpose: Admin-only endpoints for user account management and RBAC admin

@extend_schema(tags=["Users"])
class UserListCreateView(generics.ListCreateAPIView):
    """
    List existing users or create a new user.
    Strictly Admin-only access.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser, IsAdminRole]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user.
    Strictly Admin-only access.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser, IsAdminRole]

    def perform_destroy(self, instance):
        """
        Soft-delete: Deactivate the user instead of removing from DB.
        Includes a secure audit record for account revocation.
        """
        instance.is_active = False
        instance.save()
        
        record_audit_log(
            user=self.request.user,
            instance=instance,
            action=AuditLog.Action.DELETE,
            changes={"id": str(instance.id), "username": instance.username, "status": "Deactivated"}
        )
