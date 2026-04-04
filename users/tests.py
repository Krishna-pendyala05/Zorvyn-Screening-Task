import pytest
from django.urls import reverse
from users.models import User

# Domain: users | Purpose: Integration tests for RBAC on user management endpoints

@pytest.mark.django_db
class TestUserRBAC:
    def test_admin_can_list_users(self, admin_client):
        """
        Verify that ADMIN users can retrieve the user list.
        """
        url = reverse("user_list_create")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_analyst_cannot_list_users(self, analyst_client):
        """
        Verify that ANALYST users are blocked from listing users.
        """
        url = reverse("user_list_create")
        response = analyst_client.get(url)
        assert response.status_code == 403

    def test_viewer_cannot_list_users(self, viewer_client):
        """
        Verify that VIEWER users are blocked from listing users.
        """
        url = reverse("user_list_create")
        response = viewer_client.get(url)
        assert response.status_code == 403

    def test_inactive_user_cannot_access(self, api_client, inactive_user):
        """
        Verify that inactive users are blocked first, regardless of role.
        """
        api_client.force_authenticate(user=inactive_user)
        url = reverse("user_list_create")
        response = api_client.get(url)
        assert response.status_code == 403

    def test_admin_can_create_user(self, admin_client):
        """
        Verify that ADMIN can create a new user account.
        """
        url = reverse("user_list_create")
        data = {
            "username": "new_user",
            "password": "password123",
            "email": "new@zorvyn.com",
            "role": "ANALYST"
        }
        response = admin_client.post(url, data)
        assert response.status_code == 201
        assert User.objects.filter(username="new_user").exists()

@pytest.mark.django_db
class TestAuth:
    def test_login_returns_tokens(self, api_client, viewer_user):
        """
        Verify that valid credentials return JWT access and refresh tokens.
        """
        url = reverse("token_obtain_pair")
        data = {
            "username": "viewer_user",
            "password": "password123"
        }
        response = api_client.post(url, data)
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
