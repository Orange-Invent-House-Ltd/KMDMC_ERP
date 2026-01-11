from rest_framework import viewsets, status
from rest_framework.decorators import action
from utils.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
from utils.pagination import CustomPagination
from user.models import CustomUser, Department, StaffActivity, PerformanceRecord
from user.serializers.staff_profile import (
    StaffListSerializer,
    StaffProfileSerializer,
    StaffProfileUpdateSerializer
)
from console.serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing departments."""
    queryset = Department.objects.all()
    permission_classes = [AllowAny]  
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    serializer_class = DepartmentSerializer

    def list(self, request, *args, **kwargs):
        """Override list to return custom response format."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            message="Departments retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return custom response format."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Department retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        """Override create to return custom response format."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            success=True,
            message="Department created successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Override update to return custom response format."""
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
        return Response(
            success=True,
            message="Department updated successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """Override destroy to return custom response format."""
        instance = self.get_object()
        instance.delete()
        return Response(
            success=True,
            message="Department deleted successfully",
            status_code=status.HTTP_200_OK
        )


class StaffsProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Staff Profile.
    Provides detailed views for individual staff members.
    """

    permission_classes = [AllowAny]
    filterset_fields = ['department', 'role', 'location', 'is_active']
    search_fields = ['name', 'email', 'employee_id', 'position']
    ordering_fields = ['name', 'employee_id', 'created_at', 'department__name']
    ordering = ['name']
    pagination_class = CustomPagination
    queryset = CustomUser.objects.all()
    

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StaffProfileSerializer
        return StaffListSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        department_id = request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        qs = self.paginate_queryset(queryset)
        serializer = self.get_serializer(qs, many=True)
        self.pagination_class.message = "Staffs list retrieved successfully"
        response = self.get_paginated_response(
            serializer.data,
        )
        return response

    def retrieve(self, request, pk = None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(
            success=True,
            message="Staff profile retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    def patch(self, request):
        """Update current user's profile."""
        serializer = StaffProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        # Return updated profile
        profile_serializer = StaffProfileSerializer(request.user, context={'request': request})
        return Response(
            success=True,
            message='Profile updated successfully',
            data=profile_serializer.data
        )
    

