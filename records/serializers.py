from rest_framework import serializers
from .models import FinancialRecord

# Domain: records | Purpose: Validation and serialization of financial transactions


class RecordSerializer(serializers.ModelSerializer):
    # Ensures strictly typed data enters the financial pipeline and strips internal fields

    # StringRelatedField returns __str__ of the user without a nested serializer
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FinancialRecord
        fields = [
            "id", "amount", "type", "category", "date", "notes",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
        extra_kwargs = {
            "amount": {
                "help_text": "Total monetary value. Must be positive.",
                "style": {"placeholder": "1500.50"},
            },
            "category": {
                "help_text": "Domain of the record (e.g., Salary, Office, Utilities).",
                "style": {"placeholder": "Office Supplies"},
            },
            "date": {
                "help_text": "Transaction date (YYYY-MM-DD).",
                "style": {"placeholder": "2026-04-15"},
            },
            "type": {"help_text": "Classification: INCOME or EXPENSE."},
        }

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
