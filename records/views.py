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
    Analysts & Admins can read; only Admins can create.
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
        Record the creation of a financial record with accountability.
        """
        instance = serializer.save(created_by=self.request.user)
        record_audit_log(
            user=self.request.user,
            instance=instance,
            action=AuditLog.Action.CREATE,
            changes=serializer.data
        )


class RecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific financial record.
    Analysts & Admins can read; only Admins can update/delete.
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
        Record the modification of a financial record with a delta diff.
        """
        # Capture old values before saving
        old_instance = self.get_object()
        old_data = {
            "amount": str(old_instance.amount),
            "category": old_instance.category,
            "type": old_instance.type,
            "date": str(old_instance.date),
            "notes": old_instance.notes
        }
        
        instance = serializer.save()
        
        # Identify changes
        new_data = serializer.data
        changes = {
            field: [old_data[field], str(new_data[field])]
            for field in old_data
            if old_data[field] != str(new_data[field])
        }
        
        if changes:
            record_audit_log(
                user=self.request.user,
                instance=instance,
                action=AuditLog.Action.UPDATE,
                changes=changes
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
