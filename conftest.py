import pytest
from rest_framework.test import APIClient
from users.models import User
from records.models import FinancialRecord
from datetime import date

# Domain: project-root | Purpose: Shared pytest fixtures for domain-level integration testing

@pytest.fixture
def api_client():
    """
    Standard DRF API Client.
    """
    return APIClient()


@pytest.fixture
def admin_user(db):
    """
    User with ADMIN role and superuser privileges.
    """
    return User.objects.create_superuser(
        username="admin_user", 
        email="admin@zorvyn.com", 
        password="password123",
        role=User.UserRole.ADMIN
    )


@pytest.fixture
def analyst_user(db):
    """
    User with ANALYST role.
    """
    return User.objects.create_user(
        username="analyst_user", 
        email="analyst@zorvyn.com", 
        password="password123",
        role=User.UserRole.ANALYST
    )


@pytest.fixture
def viewer_user(db):
    """
    User with VIEWER role.
    """
    return User.objects.create_user(
        username="viewer_user", 
        email="viewer@zorvyn.com", 
        password="password123",
        role=User.UserRole.VIEWER
    )


@pytest.fixture
def inactive_user(db):
    """
    Inactive user (any role).
    """
    return User.objects.create_user(
        username="inactive_user", 
        email="inactive@zorvyn.com", 
        password="password123",
        role=User.UserRole.ADMIN,
        is_active=False
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    API client authenticated as ADMIN.
    """
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def analyst_client(api_client, analyst_user):
    """
    API client authenticated as ANALYST.
    """
    api_client.force_authenticate(user=analyst_user)
    return api_client


@pytest.fixture
def viewer_client(api_client, viewer_user):
    """
    API client authenticated as VIEWER.
    """
    api_client.force_authenticate(user=viewer_user)
    return api_client


@pytest.fixture
def financial_record(db):
    """
    Creates a single sample financial record.
    """
    return FinancialRecord.objects.create(
        amount="100.50",
        type=FinancialRecord.RecordType.INCOME,
        category="Sales",
        date=date(2026, 4, 1),
        notes="Q2 Launch Sale"
    )
