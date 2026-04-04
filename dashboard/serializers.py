from rest_framework import serializers

# Domain: dashboard | Purpose: Response schemas for analytical dashboard endpoints

class DashboardSummarySerializer(serializers.Serializer):
    """
    Schema for the core KPI dashboard summary.
    """
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)


class CategorySummarySerializer(serializers.Serializer):
    """
    Schema for individual category breakdowns.
    """
    category = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
