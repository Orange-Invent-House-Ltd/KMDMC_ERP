from rest_framework import viewsets, status
from rest_framework.decorators import action
from utils.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
from utils.pagination import CustomPagination
from user.models import CustomUser, Department, StaffActivity, PerformanceRecord, StaffTask
from user.serializers.staff_profile import (
    DepartmentSerializer,
    DepartmentDropdownSerializer,
    StaffListSerializer,
    StaffProfileSerializer,
    StaffProfileUpdateSerializer,
    StaffTaskSerializer,
    StaffActivitySerializer,
    PerformanceRecordSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing departments."""
    queryset = Department.objects.select_related('head', 'parent').all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'dropdown':
            return DepartmentDropdownSerializer
        return DepartmentSerializer

    @action(detail=False, methods=['get'])
    def dropdown(self, request):
        """Get departments for dropdown selection."""
        departments = self.get_queryset().filter(is_active=True)
        serializer = DepartmentDropdownSerializer(departments, many=True)
        return Response(serializer.data)

class StaffsProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Staff Profile.
    Provides detailed views for individual staff members.
    """

    permission_classes = [IsAuthenticated]
    filterset_fields = ['department', 'role', 'location', 'is_active']
    search_fields = ['name', 'email', 'employee_id', 'position']
    ordering_fields = ['name', 'employee_id', 'created_at', 'department__name']
    ordering = ['name']
    pagination_class = CustomPagination
    queryset = CustomUser.objects.filter(role = "general_staff").select_related('department', 'head').all()
    

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

    def retrieve(self, request):
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
                message="Profile update failed",
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
class StaffTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing staff tasks."""
    queryset = StaffTask.objects.select_related(
        'assigned_to', 'assigned_by', 'department'
    ).all()
    serializer_class = StaffTaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['assigned_to', 'assigned_by', 'status', 'priority', 'department']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter to show only user's tasks or tasks they assigned
        view_filter = self.request.query_params.get('filter')
        if view_filter == 'my_tasks':
            queryset = queryset.filter(assigned_to=user)
        elif view_filter == 'assigned_by_me':
            queryset = queryset.filter(assigned_by=user)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed."""
        task = self.get_object()
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        # Update user activity
        self._record_activity(task.assigned_to, 'task_completed')
        
        return Response({
            'success': True,
            'message': 'Task marked as completed'
        })

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start working on a task."""
        task = self.get_object()
        task.status = 'in_progress'
        task.save()
        
        return Response({
            'success': True,
            'message': 'Task started'
        })

    def _record_activity(self, user, activity_type):
        """Record activity for heatmap."""
        today = timezone.now().date()
        activity, created = StaffActivity.objects.get_or_create(
            user=user,
            date=today,
            defaults={'activity_count': 0}
        )
        activity.activity_count += 1
        if activity_type == 'task_completed':
            activity.tasks_completed += 1
        activity.save()
