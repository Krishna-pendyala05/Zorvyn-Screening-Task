from rest_framework.permissions import BasePermission

# Domain: users | Purpose: DRF permission classes enforcing role-based access control


class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        # Blocks inactive users before role checking reaches them
        # Every authenticated request must pass this gate first
        return bool(request.user and request.user.is_active)


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        # Dedicated gate ensuring only administrators can manage users or perform hard configuration changes
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsAnalystOrAbove(BasePermission):
    def has_permission(self, request, view):
        # Allows analysts to read financial records without granting them administrative creation rights
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ["ANALYST", "ADMIN"]
        )
