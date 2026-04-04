from django.urls import path
from .views import DashboardSummaryView, CategorySummaryView

# Domain: dashboard | Purpose: URL routing for analytical summary endpoints

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="dashboard_summary"),
    path("categories/", CategorySummaryView.as_view(), name="category_summary"),
]
