import pytest
from django.urls import reverse
from records.models import FinancialRecord
from common.models import AuditLog

# Domain: records | Purpose: Integration tests for records CRUD, RBAC, filtering, and Audit logs


@pytest.mark.django_db
class TestRecordRBAC:
    def test_admin_can_create_record(self, admin_client):
        # Ensures administrators can insert financial data securely
        url = reverse("record_list_create")
        data = {
            "amount": "500.00",
            "type": "INCOME",
            "category": "Consulting",
            "date": "2026-04-05",
        }
        response = admin_client.post(url, data)
        assert response.status_code == 201
        assert FinancialRecord.objects.filter(category="Consulting").exists()

    def test_analyst_cannot_create_record(self, analyst_client):
        # Write operations are restricted to admins to prevent data tampering
        url = reverse("record_list_create")
        data = {
            "amount": "100.00",
            "type": "EXPENSE",
            "category": "Office",
            "date": "2026-04-05",
        }
        response = analyst_client.post(url, data)
        assert response.status_code == 403

    def test_viewer_cannot_read_records(self, viewer_client):
        # Viewers only get aggregations in dashboard, never raw data rows
        url = reverse("record_list_create")
        response = viewer_client.get(url)
        assert response.status_code == 403

    def test_analyst_can_read_records(self, analyst_client, financial_record):
        # Allows analysts to review transaction history safely
        url = reverse("record_list_create")
        response = analyst_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestRecordFiltering:
    def test_filter_by_category(self, analyst_client, financial_record):
        # Validates case-insensitive exact match functionality on category fields
        url = reverse("record_list_create") + "?category=Sales"
        response = analyst_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

        url = reverse("record_list_create") + "?category=Other"
        response = analyst_client.get(url)
        assert len(response.data["results"]) == 0

    def test_filter_by_date_range(self, analyst_client, financial_record):
        # Validates temporal filtering boundaries for period reporting
        url = (
            reverse("record_list_create")
            + "?date_after=2026-04-01&date_before=2026-04-02"
        )
        response = analyst_client.get(url)
        assert len(response.data["results"]) == 1

        url = reverse("record_list_create") + "?date_after=2026-04-02"
        response = analyst_client.get(url)
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestRecordValidation:
    def test_negative_amount_fails(self, admin_client):
        # Guarantees mathematical invariants are enforced at the API boundary
        url = reverse("record_list_create")
        data = {
            "amount": "-100.00",
            "type": "EXPENSE",
            "category": "Office",
            "date": "2026-04-05",
        }
        response = admin_client.post(url, data)
        assert response.status_code == 400
        assert "amount" in response.data


@pytest.mark.django_db
class TestRecordAccountability:
    def test_record_creation_assigns_creator(self, admin_client):
        # Ensures every transaction traces explicitly back to the issuing user
        url = reverse("record_list_create")
        data = {
            "amount": "750.00",
            "type": "INCOME",
            "category": "Bonus",
            "date": "2026-04-10",
        }
        response = admin_client.post(url, data)
        assert response.status_code == 201

        record = FinancialRecord.objects.get(id=response.data["id"])
        assert response.data["created_by"] == "admin_user (ADMIN)"
        assert record.created_by.username == "admin_user"


@pytest.mark.django_db
class TestRecordAudit:
    def test_update_generates_json_diff(self, admin_client, financial_record):
        # Validates precision of the JSON delta tracking engine
        url = reverse("record_detail", kwargs={"pk": financial_record.id})
        old_amount = str(financial_record.amount)
        new_amount = "999.99"

        response = admin_client.patch(url, {"amount": new_amount})
        assert response.status_code == 200

        audit = AuditLog.objects.filter(
            object_id=financial_record.id, action=AuditLog.Action.UPDATE
        ).first()

        assert audit is not None
        assert "amount" in audit.changes
        assert audit.changes["amount"] == [old_amount, new_amount]
        assert "category" not in audit.changes

    def test_soft_delete_preserves_data(self, admin_client, financial_record):
        # Ensures destructive actions only flag records rather than dropping rows
        url = reverse("record_detail", kwargs={"pk": financial_record.id})

        response = admin_client.delete(url)
        assert response.status_code == 204

        assert FinancialRecord.objects.filter(id=financial_record.id).count() == 0
        assert FinancialRecord.all_objects.filter(id=financial_record.id).exists()

        assert AuditLog.objects.filter(
            object_id=financial_record.id, action=AuditLog.Action.DELETE
        ).exists()
