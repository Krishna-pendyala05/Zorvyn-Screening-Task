from django.db import transaction
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import FinancialRecord
from .serializers import RecordSerializer
from .filters import RecordFilter
from users.permissions import IsActiveUser, IsAdminRole, IsAnalystOrAbove
from common.utils import record_audit_log, compute_delta
from common.models import AuditLog

# Domain: records | Purpose: Financial record CRUD with per-method RBAC enforcement


@extend_schema(tags=["Records"])
class RecordListCreateView(generics.ListCreateAPIView):
    # Ingestion point for appending verified financial events to the database
    queryset = FinancialRecord.objects.all()
    serializer_class = RecordSerializer
    filterset_class = RecordFilter

    def get_permissions(self):
        # Writers must be ADMIN; readers need ANALYST or above (VIEWER is excluded)
        if self.request.method == "GET":
            return [IsActiveUser(), IsAnalystOrAbove()]
        return [IsActiveUser(), IsAdminRole()]

    def perform_create(self, serializer):
        # Atomic: if the audit INSERT fails the record INSERT is rolled back too
        with transaction.atomic():
            instance = serializer.save(created_by=self.request.user)
            record_audit_log(
                user=self.request.user,
                instance=instance,
                action=AuditLog.Action.CREATE,
                changes=serializer.data,
            )


@extend_schema(tags=["Records"])
class RecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Handles surgical targeted modifications and non-destructive soft deletions
    queryset = FinancialRecord.objects.all()
    serializer_class = RecordSerializer

    def get_permissions(self):
        # Writers must be ADMIN; readers need ANALYST or above (VIEWER is excluded)
        if self.request.method == "GET":
            return [IsActiveUser(), IsAnalystOrAbove()]
        return [IsActiveUser(), IsAdminRole()]

    def perform_update(self, serializer):
        # Atomic: delta computation, save, and audit log are one unit
        with transaction.atomic():
            old = self.get_object()
            old_data = {
                "amount": str(old.amount),
                "category": old.category,
                "type": old.type,
                "date": str(old.date),
                "notes": old.notes,
            }
            instance = serializer.save()
            new_data = {
                "amount": str(instance.amount),
                "category": instance.category,
                "type": instance.type,
                "date": str(instance.date),
                "notes": instance.notes,
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
        # Atomic: audit log and soft-delete are one unit — no orphaned log on failure
        with transaction.atomic():
            record_audit_log(
                user=self.request.user,
                instance=instance,
                action=AuditLog.Action.DELETE,
                changes={"id": str(instance.id), "amount": str(instance.amount)},
            )
            instance.delete()
