import pytest
from django.urls import reverse
from records.models import FinancialRecord
from common.models import AuditLog

# Domain: records | Purpose: Integration tests for records CRUD, RBAC, filtering, and Audit logs

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
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestRecordFiltering:
    """
    Verify filtering logic for the list endpoint.
    """
    def test_filter_by_category(self, analyst_client, financial_record):
        url = reverse("record_list_create") + "?category=Sales"
        response = analyst_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        
        url = reverse("record_list_create") + "?category=Other"
        response = analyst_client.get(url)
        assert len(response.data["results"]) == 0

    def test_filter_by_date_range(self, analyst_client, financial_record):
        url = reverse("record_list_create") + "?date_after=2026-04-01&date_before=2026-04-02"
        response = analyst_client.get(url)
        assert len(response.data["results"]) == 1
        
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


@pytest.mark.django_db
class TestRecordAccountability:
    """
    Verify accountability and ownership tracking.
    """
    def test_record_creation_assigns_creator(self, admin_client):
        url = reverse("record_list_create")
        data = {
            "amount": "750.00", 
            "type": "INCOME", 
            "category": "Bonus", 
            "date": "2026-04-10"
        }
        response = admin_client.post(url, data)
        assert response.status_code == 201
        
        record = FinancialRecord.objects.get(id=response.data["id"])
        # StringRelatedField returns the user's __str__ representation
        assert response.data["created_by"] == "admin_user (ADMIN)"
        assert record.created_by.username == "admin_user"


@pytest.mark.django_db
class TestRecordAudit:
    """
    Verify high-precision audit logging and soft-deletion.
    """
    def test_update_generates_json_diff(self, admin_client, financial_record):
        url = reverse("record_detail", kwargs={"pk": financial_record.id})
        old_amount = str(financial_record.amount)
        new_amount = "999.99"
        
        response = admin_client.patch(url, {"amount": new_amount})
        assert response.status_code == 200
        
        audit = AuditLog.objects.filter(
            object_id=financial_record.id, 
            action=AuditLog.Action.UPDATE
        ).first()
        
        assert audit is not None
        assert "amount" in audit.changes
        assert audit.changes["amount"] == [old_amount, new_amount]
        assert "category" not in audit.changes

    def test_soft_delete_preserves_data(self, admin_client, financial_record):
        url = reverse("record_detail", kwargs={"pk": financial_record.id})
        
        response = admin_client.delete(url)
        assert response.status_code == 204
        
        assert FinancialRecord.objects.filter(id=financial_record.id).count() == 0
        assert FinancialRecord.all_objects.filter(id=financial_record.id).exists()
        
        assert AuditLog.objects.filter(
            object_id=financial_record.id, 
            action=AuditLog.Action.DELETE
        ).exists()
