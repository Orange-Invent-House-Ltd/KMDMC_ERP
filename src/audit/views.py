# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets

from audit.models import AuditLog
from audit.filters import AuditLogFilter
from audit.serializers import AuditLogSerializer
from console.permissions import IsSuperAdmin, permissions_required
from rest_framework.permissions import AllowAny
from utils.pagination import CustomPagination
from utils.permissions import PERMISSIONS
from utils.response import Response


class AuditLogViewSets(viewsets.ModelViewSet):
    """Admin Audit Log"""

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)
    http_method_names = ["get"]
    filter_backends = [
        # DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = AuditLogFilter
    search_fields = ["user_name", "user_email", "action", "audit_type"]
    ordering_fields = ["created_at"]

    
    def list(self, request, *args, **kwargs):
        try:
            filtered_queryset = self.filter_queryset(self.get_queryset())
            qs = self.paginate_queryset(filtered_queryset)
            serializer = self.get_serializer(qs, many=True)
            self.pagination_class.message = (
                "Audit trail records retrieved successfully."
            )
            response = self.get_paginated_response(serializer.data)
            return response

        except Exception as e:
            return Response(
                success=False,
                message=f"Unexpected error occurred. {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Audit trail record retrieved successfully.",
            data=serializer.data,
        )
