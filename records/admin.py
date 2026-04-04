from django.contrib import admin
from .models import FinancialRecord

# Domain: records | Purpose: Admin interface configuration for financial transaction oversight

@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    """
    Customized Admin interface for the FinancialRecord model.
    """
    list_display = ("id", "amount", "type", "category", "date")
    list_filter = ("type", "category", "date")
    search_fields = ("category", "notes")
    ordering = ("-date",)

    # Make the IDs read-only since they are auto-generated UUIDs
    readonly_fields = ("id", "created_at", "updated_at")
