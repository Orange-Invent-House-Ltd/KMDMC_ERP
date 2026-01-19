from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from rest_framework import filters

from utils.response import Response
from utils.pagination import CustomPagination
from console.permissions import IsSuperAdmin
from hr_config.models import LeaveType
from hr_config.serializers import (
    LeaveTypeListSerializer,
    LeaveTypeDetailSerializer,
    LeaveTypeCreateSerializer,
    LeaveTypeUpdateSerializer,
)
from console.permissions import permissions_required
from utils.permissions import PERMISSIONS

class LeaveTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave types.
    HR admins can manage, all staff can view.
    """
    queryset = LeaveType.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['accrual_frequency', 'is_paid', 'is_active']
    search_fields = ['leave_type_name', 'description']
    ordering_fields = ['leave_type_name', 'allowance_days', 'created_at']
    ordering = ['leave_type_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return LeaveTypeListSerializer
        elif self.action == 'retrieve':
            return LeaveTypeDetailSerializer
        elif self.action == 'create':
            return LeaveTypeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LeaveTypeUpdateSerializer
        return LeaveTypeListSerializer

    def get_permissions(self):
        """Only admins can create/update/delete, all authenticated users can view."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated()]

    @permissions_required([PERMISSIONS.CAN_ACCESS_HR_CONFIG])
    def list(self, request, *args, **kwargs):
        """List all leave types."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            message="Leave types retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @permissions_required([PERMISSIONS.CAN_ACCESS_HR_CONFIG])
    def retrieve(self, request, *args, **kwargs):
        """Retrieve single leave type."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Leave type retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @permissions_required([PERMISSIONS.CAN_ACCESS_HR_CONFIG])
    def create(self, request, *args, **kwargs):
        """Create new leave type."""
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        # Return full details
        leave_type = LeaveType.objects.get(pk=serializer.instance.pk)
        response_serializer = LeaveTypeDetailSerializer(leave_type)

        return Response(
            success=True,
            message="Leave type created successfully",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    @permissions_required([PERMISSIONS.CAN_ACCESS_HR_CONFIG])
    def update(self, request, *args, **kwargs):
        """Update leave type."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        # Return full details
        instance.refresh_from_db()
        response_serializer = LeaveTypeDetailSerializer(instance)

        return Response(
            success=True,
            message="Leave type updated successfully",
            data=response_serializer.data,
            status_code=status.HTTP_200_OK
        )

    @permissions_required([PERMISSIONS.CAN_ACCESS_HR_CONFIG])
    def destroy(self, request, *args, **kwargs):
        """Delete leave type."""
        instance = self.get_object()
        leave_type_name = instance.leave_type_name
        instance.delete()

        return Response(
            success=True,
            message=f"Leave type '{leave_type_name}' deleted successfully",
            status_code=status.HTTP_200_OK
        )
