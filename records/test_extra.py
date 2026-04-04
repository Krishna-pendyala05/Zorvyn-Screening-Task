import pytest
from django.urls import reverse
from records.models import FinancialRecord
from common.models import AuditLog

# Domain: records | Purpose: Advanced verification for soft-deletion and audit logging

@pytest.mark.django_db
def test_soft_delete_record(admin_client, financial_record):
    """
    Verify that deleting a record marks it as deleted instead of removing it.
    """
    url = reverse("user_detail", kwargs={"pk": financial_record.id}) # Oops, should be record_detail
    # Correcting the URL name
    url = reverse("record_detail", kwargs={"pk": financial_record.id})
    
    response = admin_client.delete(url)
    assert response.status_code == 204
    
    # Check that it's gone from standard objects
    assert FinancialRecord.objects.count() == 0
    
    # Check that it still exists in all_objects
    assert FinancialRecord.all_objects.filter(id=financial_record.id).exists()
    
    # Verify AuditLog entry
    assert AuditLog.objects.filter(
        model_name="FinancialRecord", 
        object_id=financial_record.id,
        action=AuditLog.Action.DELETE
    ).exists()

@pytest.mark.django_db
def test_audit_log_on_create(admin_client):
    """
    Verify that creating a record generates an audit log.
    """
    url = reverse("record_list_create")
    data = {
        "amount": "500.00",
        "type": "INCOME",
        "category": "Bonus",
        "date": "2026-05-01"
    }
    
    response = admin_client.post(url, data)
    assert response.status_code == 201
    
    record_id = response.data["id"]
    assert AuditLog.objects.filter(
        model_name="FinancialRecord",
        object_id=record_id,
        action=AuditLog.Action.CREATE
    ).exists()

@pytest.mark.django_db
def test_soft_delete_user(admin_client, analyst_user):
    """
    Verify that deleting a user deactivates them instead of removing them.
    """
    url = reverse("user_detail", kwargs={"pk": analyst_user.id})
    
    response = admin_client.delete(url)
    assert response.status_code == 204
    
    analyst_user.refresh_from_db()
    assert analyst_user.is_active is False
