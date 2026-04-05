import pytest
from django.urls import reverse
from records.models import FinancialRecord

# Domain: dashboard | Purpose: Integration tests for analytical aggregation logic


@pytest.mark.django_db
class TestDashboardAggregation:
    def test_summary_calculation(self, viewer_client, db):
        # Ensures ORM calculates distinct aggregates over income vs expense cleanly
        FinancialRecord.objects.create(
            amount="100.00", type="INCOME", category="Sales", date="2026-04-01"
        )
        FinancialRecord.objects.create(
            amount="200.00", type="INCOME", category="Consulting", date="2026-04-01"
        )
        FinancialRecord.objects.create(
            amount="50.00", type="EXPENSE", category="Office", date="2026-04-01"
        )

        url = reverse("dashboard_summary")
        response = viewer_client.get(url)

        assert response.status_code == 200
        assert response.data["total_income"] == "300.00"
        assert response.data["total_expenses"] == "50.00"
        assert response.data["net_balance"] == "250.00"

    def test_category_breakdown(self, analyst_client, db):
        # Validates GROUP BY summation properly segments financial groups
        FinancialRecord.objects.create(
            amount="100.00", type="INCOME", category="Sales", date="2026-04-01"
        )
        FinancialRecord.objects.create(
            amount="50.00", type="INCOME", category="Sales", date="2026-04-01"
        )
        FinancialRecord.objects.create(
            amount="75.00", type="EXPENSE", category="Rent", date="2026-04-01"
        )

        url = reverse("category_summary")
        response = analyst_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2

        assert response.data[0]["category"] == "Sales"
        assert response.data[0]["total_amount"] == "150.00"
        assert response.data[0]["record_count"] == 2

    def test_unauthenticated_access_denied(self, api_client):
        # Guard mechanism ensuring aggregation metrics never leak publicly
        url = reverse("dashboard_summary")
        response = api_client.get(url)
        assert response.status_code == 401
