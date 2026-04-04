from rest_framework import serializers
from .models import FinancialRecord

# Domain: records | Purpose: Serialization of financial record records with data integrity

class RecordSerializer(serializers.ModelSerializer):
    """
    Serializer for the FinancialRecord model.
    Handles data validation for financial transactions.
    """
    class Meta:
        model = FinancialRecord
        fields = ["id", "amount", "type", "category", "date", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "amount": {
                "help_text": "Total monetary value of the record. Must be positive.",
                "style": {"placeholder": "1500.50"}
            },
            "category": {
                "help_text": "Specific domain for the record (e.g., Salary, Office, Utilities).",
                "style": {"placeholder": "Office Supplies"}
            },
            "date": {
                "help_text": "The billing or transaction date (YYYY-MM-DD).",
                "style": {"placeholder": "2026-04-15"}
            },
            "type": {
                "help_text": "Classification: INCOME or EXPENSE."
            }
        }

    def validate_amount(self, value):
        """
        Verify that the financial amount is always positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
