from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer
from .permissions import IsActiveUser, IsAdminRole

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
    Retrieve, update, or delete a specific user account.
    Strictly Admin-only access.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser, IsAdminRole]

    def perform_destroy(self, instance):
        """
        Optional: Implement prevention of self-deletion logic here in Phase 5.
        """
        super().perform_destroy(instance)
