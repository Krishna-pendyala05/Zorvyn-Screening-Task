from django.urls import path
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserListCreateView, UserDetailView

# Domain: users | Purpose: URL routing for authentication and user management

# Wrap third-party JWT views to attach them to the Auth OpenAPI tag
TokenObtainPairView = extend_schema_view(
    post=extend_schema(tags=["Auth"], summary="Login & Obtain Token")
)(TokenObtainPairView)

TokenRefreshView = extend_schema_view(
    post=extend_schema(tags=["Auth"], summary="Refresh Access Token")
)(TokenRefreshView)

urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", UserListCreateView.as_view(), name="user_list_create"),
    path("<uuid:pk>/", UserDetailView.as_view(), name="user_detail"),
]
