import pytest
from rest_framework.test import APIClient
from users.models import User
from records.models import FinancialRecord
from datetime import date

# Domain: project-root | Purpose: Shared pytest fixtures for integration testing


@pytest.fixture
def api_client():
    # Base unauthenticated DRF client for test requests
    return APIClient()


@pytest.fixture
def admin_user(db):
    # Simulates an administrator with unrestricted forensic and modification access
    return User.objects.create_superuser(
        username="admin_user",
        email="admin@zorvyn.com",
        password="password123",
        role=User.UserRole.ADMIN,
    )


@pytest.fixture
def analyst_user(db):
    # Simulates a staff analyst with broad read access but restricted write access
    return User.objects.create_user(
        username="analyst_user",
        email="analyst@zorvyn.com",
        password="password123",
        role=User.UserRole.ANALYST,
    )


@pytest.fixture
def viewer_user(db):
    # Simulates a read-only stakeholder restricted entirely to the dashboard
    return User.objects.create_user(
        username="viewer_user",
        email="viewer@zorvyn.com",
        password="password123",
        role=User.UserRole.VIEWER,
    )


@pytest.fixture
def inactive_user(db):
    # Allows verifying that the underlying account status gate works independent of RBAC
    return User.objects.create_user(
        username="inactive_user",
        email="inactive@zorvyn.com",
        password="password123",
        role=User.UserRole.ADMIN,
        is_active=False,
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    # Forces authentication so tests don't need to manually acquire JWTs
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def analyst_client(api_client, analyst_user):
    api_client.force_authenticate(user=analyst_user)
    return api_client


@pytest.fixture
def viewer_client(api_client, viewer_user):
    api_client.force_authenticate(user=viewer_user)
    return api_client


@pytest.fixture
def financial_record(db):
    # Provides a baseline transaction target for patch and delete integrity testing
    return FinancialRecord.objects.create(
        amount="100.50",
        type=FinancialRecord.RecordType.INCOME,
        category="Sales",
        date=date(2026, 4, 1),
        notes="Q2 Launch Sale",
    )
