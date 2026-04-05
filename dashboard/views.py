from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db.models import Sum, Count
from records.models import FinancialRecord
from users.permissions import IsActiveUser
from .serializers import DashboardSummarySerializer, CategorySummarySerializer
from rest_framework.exceptions import ValidationError

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
                "net_balance": "9499.75",
            },
            response_only=True,
        )
    ],
)
class DashboardSummaryView(APIView):
    # Aggregates high-level statistical snapshots across the complete transaction history
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        date_after = request.query_params.get("date_after")
        date_before = request.query_params.get("date_before")

        queryset = FinancialRecord.objects.all()

        try:
            if date_after:
                queryset = queryset.filter(date__gte=date_after)
            if date_before:
                queryset = queryset.filter(date__lte=date_before)
            # Evaluate the queryset immediately to catch parse errors before aggregation
            queryset.exists()
        except ValueError:
            # Prevents 500 errors on invalid date format input
            raise ValidationError({"detail": "Invalid date format. Use YYYY-MM-DD."})

        # Aggregation at DB level avoids loading heavy datasets into memory
        income = queryset.filter(type=FinancialRecord.RecordType.INCOME).aggregate(
            total=Sum("amount")
        )["total"] or 0

        expenses = queryset.filter(type=FinancialRecord.RecordType.EXPENSE).aggregate(
            total=Sum("amount")
        )["total"] or 0

        return Response(
            {
                "total_income": f"{income:.2f}",
                "total_expenses": f"{expenses:.2f}",
                "net_balance": f"{(income - expenses):.2f}",
            }
        )


@extend_schema(
    tags=["Dashboard"],
    responses={200: CategorySummarySerializer(many=True)},
    examples=[
        OpenApiExample(
            "Categorical Breakdown",
            value=[
                {"category": "Salary", "total_amount": "12000.00", "record_count": 1},
                {"category": "Office", "total_amount": "450.00", "record_count": 3},
                {"category": "Travel", "total_amount": "1200.00", "record_count": 1},
            ],
            response_only=True,
        )
    ],
)
class CategorySummaryView(APIView):
    # Groups financial volumes by domain taxonomy to feed dashboard visualizations
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        summary = (
            FinancialRecord.objects.values("category")
            .annotate(total_amount=Sum("amount"), record_count=Count("id"))
            .order_by("-total_amount")
        )

        # Passes through serializer to ensure schema match and consistent typing
        return Response(CategorySummarySerializer(summary, many=True).data)
