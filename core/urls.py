from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

# Domain: core | Purpose: Root URL dispatcher for all domain apps and API docs

urlpatterns = [
    # Root Redirect to Docs
    path("", RedirectView.as_view(url="api/schema/swagger-ui/"), name="root-redirect"),
    
    path("admin/", admin.site.urls),
    # API Schema / Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Domain Apps
    path("api/users/", include("users.urls")),
    path("api/records/", include("records.urls")),
    path("api/dashboard/", include("dashboard.urls")),
]
