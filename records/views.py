from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import FinancialRecord
from .serializers import RecordSerializer
from .filters import RecordFilter
from users.permissions import IsActiveUser, IsAdminRole, IsAnalystOrAbove
from common.utils import record_audit_log
from common.models import AuditLog

# Domain: records | Purpose: Financial record management endpoints with RBAC enforcement

@extend_schema(tags=["Records"])
class RecordListCreateView(generics.ListCreateAPIView):
    """
    List existing financial records or create a new record.
    Analysts can read; Admins can create.
    """
    queryset = FinancialRecord.objects.all()
    serializer_class = RecordSerializer
    filterset_class = RecordFilter
    
    def get_permissions(self):
        """
        RBAC Mapping:
        - GET: IsAnalystOrAbove (Viewer excluded)
        - POST: IsAdminRole
        """
        if self.request.method == "GET":
            return [IsActiveUser(), IsAnalystOrAbove()]
        return [IsActiveUser(), IsAdminRole()]

    def perform_create(self, serializer):
        """
        Record the creation of a financial record.
        """
        instance = serializer.save()
        record_audit_log(
            user=self.request.user,
            instance=instance,
            action=AuditLog.Action.CREATE,
            changes=serializer.data
        )


class RecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific financial record.
    Analysts can read; Admins can update/delete.
    """
    queryset = FinancialRecord.objects.all()
    serializer_class = RecordSerializer
    
    def get_permissions(self):
        """
        RBAC Mapping:
        - GET: IsAnalystOrAbove (Viewer excluded)
        - PATCH/PUT/DELETE: IsAdminRole
        """
        if self.request.method == "GET":
            return [IsActiveUser(), IsAnalystOrAbove()]
        return [IsActiveUser(), IsAdminRole()]

    def perform_update(self, serializer):
        """
        Record the modification of a financial record.
        """
        # Capture old state if needed, here we just log the new set
        instance = serializer.save()
        record_audit_log(
            user=self.request.user,
            instance=instance,
            action=AuditLog.Action.UPDATE,
            changes=serializer.data
        )

    def perform_destroy(self, instance):
        """
        Record the deletion of a financial record.
        """
        record_audit_log(
            user=self.request.user,
            instance=instance,
            action=AuditLog.Action.DELETE,
            changes={"id": str(instance.id), "amount": str(instance.amount)}
        )
        instance.delete()
