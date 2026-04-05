from django.contrib import admin
from .models import FinancialRecord

# Domain: records | Purpose: Admin interface for financial transaction oversight


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    # Emergency interface for untangling bad categorizations while preventing untracked data loss
    list_display = ("id", "amount", "type", "category", "date")
    list_filter = ("type", "category", "date")
    search_fields = ("category", "notes")
    ordering = ("-date",)
    readonly_fields = ("id", "created_at", "updated_at", "created_by")

    def save_model(self, request, obj, form, change):
        from common.utils import record_audit_log, compute_delta
        from common.models import AuditLog

        if not getattr(obj, "created_by_id", None):
            obj.created_by = request.user

        if not change:
            super().save_model(request, obj, form, change)
            record_audit_log(
                user=request.user,
                instance=obj,
                action=AuditLog.Action.CREATE,
                changes={
                    "amount": str(obj.amount),
                    "type": obj.type,
                    "category": obj.category,
                    "date": str(obj.date),
                    "notes": obj.notes,
                },
            )
        else:
            old_obj = FinancialRecord.objects.get(pk=obj.pk)
            old_data = {
                "amount": str(old_obj.amount),
                "type": old_obj.type,
                "category": old_obj.category,
                "date": str(old_obj.date),
                "notes": old_obj.notes,
            }
            super().save_model(request, obj, form, change)
            new_data = {
                "amount": str(obj.amount),
                "type": obj.type,
                "category": obj.category,
                "date": str(obj.date),
                "notes": obj.notes,
            }
            changes = compute_delta(old_data, new_data)
            if changes:
                record_audit_log(
                    user=request.user,
                    instance=obj,
                    action=AuditLog.Action.UPDATE,
                    changes=changes,
                )

    def delete_model(self, request, obj):
        from common.utils import record_audit_log
        from common.models import AuditLog

        record_audit_log(
            user=request.user,
            instance=obj,
            action=AuditLog.Action.DELETE,
            changes={"id": str(obj.id), "amount": str(obj.amount)},
        )
        super().delete_model(request, obj)
