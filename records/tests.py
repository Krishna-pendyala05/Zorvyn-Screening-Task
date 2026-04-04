import pytest
from django.urls import reverse
from records.models import FinancialRecord

# Domain: records | Purpose: Integration tests for records CRUD, RBAC, and filtering

@pytest.mark.django_db
class TestRecordRBAC:
    """
    Verify RBAC enforcement on record endpoints.
    """
    def test_admin_can_create_record(self, admin_client):
        url = reverse("record_list_create")
        data = {
            "amount": "500.00",
            "type": "INCOME",
            "category": "Consulting",
            "date": "2026-04-05"
        }
        response = admin_client.post(url, data)
        assert response.status_code == 201
        assert FinancialRecord.objects.filter(category="Consulting").exists()

    def test_analyst_cannot_create_record(self, analyst_client):
        url = reverse("record_list_create")
        data = {
            "amount": "100.00", 
            "type": "EXPENSE", 
            "category": "Office", 
            "date": "2026-04-05"
        }
        response = analyst_client.post(url, data)
        assert response.status_code == 403

    def test_viewer_cannot_read_records(self, viewer_client):
        url = reverse("record_list_create")
        response = viewer_client.get(url)
        assert response.status_code == 403

    def test_analyst_can_read_records(self, analyst_client, financial_record):
        url = reverse("record_list_create")
        response = analyst_client.get(url)
        assert response.status_code == 200
        # Results are paginated by default in core.settings
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestRecordFiltering:
    """
    Verify filtering logic for the list endpoint.
    """
    def test_filter_by_category(self, analyst_client, financial_record):
        # Exact match
        url = reverse("record_list_create") + "?category=Sales"
        response = analyst_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        
        # No match
        url = reverse("record_list_create") + "?category=Other"
        response = analyst_client.get(url)
        assert len(response.data["results"]) == 0

    def test_filter_by_date_range(self, analyst_client, financial_record):
        # financial_record date is 2026-04-01
        url = reverse("record_list_create") + "?date_after=2026-04-01&date_before=2026-04-02"
        response = analyst_client.get(url)
        assert len(response.data["results"]) == 1
        
        # Out of range
        url = reverse("record_list_create") + "?date_after=2026-04-02"
        response = analyst_client.get(url)
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestRecordValidation:
    """
    Verify serializer-level and model-level validation.
    """
    def test_negative_amount_fails(self, admin_client):
        url = reverse("record_list_create")
        data = {
            "amount": "-100.00", 
            "type": "EXPENSE", 
            "category": "Office", 
            "date": "2026-04-05"
        }
        response = admin_client.post(url, data)
        assert response.status_code == 400
        assert "amount" in response.data
