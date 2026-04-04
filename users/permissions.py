from rest_framework.permissions import BasePermission

# Domain: users | Purpose: DRF permission classes enforcing role-based access control (RBAC)

class IsActiveUser(BasePermission):
    """
    Blocks inactive users before role checking reaches them.
    Every authenticated request must pass this gate first.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active)


class IsAdminRole(BasePermission):
    """
    Allows access only to users with the ADMIN role.
    Used for user management and record modifications (Phase 3).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'ADMIN'
        )


class IsAnalystOrAbove(BasePermission):
    """
    Allows access to users with either ANALYST or ADMIN roles.
    Used for reading financial records (Phase 3).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['ANALYST', 'ADMIN']
        )
