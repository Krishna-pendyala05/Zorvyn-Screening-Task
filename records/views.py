from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import FinancialRecord
from .serializers import RecordSerializer
from .filters import RecordFilter
from users.permissions import IsActiveUser, IsAdminRole, IsAnalystOrAbove

# Domain: records | Purpose: Financial record management endpoints with RBAC enforcement

@extend_schema(tags=["Records"])
class RecordListCreateView(generics.ListCreateAPIView):
    """
    List existing financial records or create a new record.
    Analysts can read; Admins can create.
    """
    queryset = FinancialRecord.objects.all()
    serializer_class = RecordSerializer
    filterset_class = RecordFilter
    
    def get_permissions(self):
        """
        RBAC Mapping:
        - GET: IsAnalystOrAbove (Viewer excluded)
        - POST: IsAdminRole
        """
        if self.request.method == "GET":
            return [IsActiveUser(), IsAnalystOrAbove()]
        return [IsActiveUser(), IsAdminRole()]


class RecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific financial record.
    Analysts can read; Admins can update/delete.
    """
    queryset = FinancialRecord.objects.all()
    serializer_class = RecordSerializer
    
    def get_permissions(self):
        """
        RBAC Mapping:
        - GET: IsAnalystOrAbove (Viewer excluded)
        - PATCH/PUT/DELETE: IsAdminRole
        """
        if self.request.method == "GET":
            return [IsActiveUser(), IsAnalystOrAbove()]
        return [IsActiveUser(), IsAdminRole()]
