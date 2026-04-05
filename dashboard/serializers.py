from rest_framework import serializers

# Domain: dashboard | Purpose: Response schemas for analytical dashboard endpoints


class DashboardSummarySerializer(serializers.Serializer):
    # Enforces type coercion and standardizes response payloads for main dashboard metrics
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)


class CategorySummarySerializer(serializers.Serializer):
    # Structures aggregated categorization data explicitly for OpenAPI consumer schemas
    category = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    record_count = serializers.IntegerField()
