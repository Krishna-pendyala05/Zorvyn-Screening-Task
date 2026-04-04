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
        fields = (
            "id", 
            "amount", 
            "type", 
            "category", 
            "date", 
            "notes", 
            "created_at", 
            "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_amount(self, value):
        """
        Verify that the financial amount is always positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
