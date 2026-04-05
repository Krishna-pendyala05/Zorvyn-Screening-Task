import pytest
from django.urls import reverse
from users.models import User

# Domain: users | Purpose: Integration tests for RBAC on user management endpoints


@pytest.mark.django_db
class TestUserRBAC:
    def test_admin_can_list_users(self, admin_client):
        # Admin needs unrestricted visibility of the user directory for access provisioning
        url = reverse("user_list_create")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_admin_can_deactivate_user(self, admin_client, analyst_user):
        # Validates soft-deletion mechanism prevents hard data loss
        url = reverse("user_detail", kwargs={"pk": analyst_user.id})
        response = admin_client.delete(url)
        assert response.status_code == 204

        analyst_user.refresh_from_db()
        assert analyst_user.is_active is False

    def test_analyst_cannot_list_users(self, analyst_client):
        # Analysts are restricted from user management to maintain strict separation of concerns
        url = reverse("user_list_create")
        response = analyst_client.get(url)
        assert response.status_code == 403

    def test_viewer_cannot_list_users(self, viewer_client):
        # Viewers must be blocked entirely from management endpoints
        url = reverse("user_list_create")
        response = viewer_client.get(url)
        assert response.status_code == 403

    def test_inactive_user_cannot_access(self, api_client, inactive_user):
        # Ensures deactivated tokens fail before reaching any domain logic
        api_client.force_authenticate(user=inactive_user)
        url = reverse("user_list_create")
        response = api_client.get(url)
        assert response.status_code == 403

    def test_admin_can_create_user(self, admin_client):
        # Allows admins to provision new accounts with defined roles
        url = reverse("user_list_create")
        data = {
            "username": "new_user",
            "password": "password123",
            "email": "new@zorvyn.com",
            "role": "ANALYST",
        }
        response = admin_client.post(url, data)
        assert response.status_code == 201
        assert User.objects.filter(username="new_user").exists()


@pytest.mark.django_db
class TestAuth:
    def test_login_returns_tokens(self, api_client, viewer_user):
        # Valid credentials must return JWT payload for stateless session management
        url = reverse("token_obtain_pair")
        data = {"username": "viewer_user", "password": "password123"}
        response = api_client.post(url, data)
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
