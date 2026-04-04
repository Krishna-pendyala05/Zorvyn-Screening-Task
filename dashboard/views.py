from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db.models import Sum, Count
from records.models import FinancialRecord
from users.permissions import IsActiveUser
from .serializers import DashboardSummarySerializer, CategorySummarySerializer

# Domain: dashboard | Purpose: Analytical endpoints for financial summaries and categorization

@extend_schema(
    tags=["Dashboard"],
    responses={200: DashboardSummarySerializer},
    examples=[
        OpenApiExample(
            "Successful Summary",
            value={
                "total_income": "15000.00",
                "total_expenses": "5500.25",
                "net_balance": "9499.75"
            },
            response_only=True,
        )
    ]
)
class DashboardSummaryView(APIView):
    """
    Calculates key financial metrics: income, expenses, and net balance.
    Supports date range filtering. Accessible to all authenticated roles.
    """
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        # Apply date filters if provided
        date_after = request.query_params.get("date_after")
        date_before = request.query_params.get("date_before")
        
        queryset = FinancialRecord.objects.all()
        if date_after:
            queryset = queryset.filter(date__gte=date_after)
        if date_before:
            queryset = queryset.filter(date__lte=date_before)

        # Database-level aggregation for efficiency
        income = queryset.filter(
            type=FinancialRecord.RecordType.INCOME
        ).aggregate(total=Sum("amount"))["total"] or 0
        
        expenses = queryset.filter(
            type=FinancialRecord.RecordType.EXPENSE
        ).aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "total_income": f"{income:.2f}",
            "total_expenses": f"{expenses:.2f}",
            "net_balance": f"{(income - expenses):.2f}"
        })


@extend_schema(
    tags=["Dashboard"],
    responses={200: CategorySummarySerializer(many=True)},
    examples=[
        OpenApiExample(
            "Categorical Breakdown",
            value=[
                {"category": "Salary", "total_amount": "12000.00", "record_count": 1},
                {"category": "Office", "total_amount": "450.00", "record_count": 3},
                {"category": "Travel", "total_amount": "1200.00", "record_count": 1}
            ],
            response_only=True,
        )
    ]
)
class CategorySummaryView(APIView):
    """
    Groups transactions by category to visualize spending/earning patterns.
    Returns sorted list of category-wise totals.
    """
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        # Use values and annotate for GroupBy logic
        summary = FinancialRecord.objects.values("category").annotate(
            total_amount=Sum("amount"),
            transaction_count=Count("id")
        ).order_by("-total_amount")
        
        return Response(summary)
