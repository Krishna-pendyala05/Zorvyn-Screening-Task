from django.urls import path
from .views import RecordListCreateView, RecordDetailView

# Domain: records | Purpose: URL routing for financial records CRUD

urlpatterns = [
    path("", RecordListCreateView.as_view(), name="record_list_create"),
    path("<uuid:pk>/", RecordDetailView.as_view(), name="record_detail"),
]
