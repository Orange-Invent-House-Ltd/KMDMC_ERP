from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from utils.response import Response

from tasks.models import Task
from tasks.serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskStatusUpdateSerializer,
    TaskAdminUpdateSerializer,
)
from console.permissions import permissions_required
from utils.permissions import PERMISSIONS


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.select_related('assigned_to', 'assigned_by').all()
    filterset_fields = ['assigned_to', 'assigned_by', 'status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            # Check if user is admin
            user = self.request.user
            if user.is_authenticated and (user.is_admin or user.is_superuser or user.is_staff):
                return TaskAdminUpdateSerializer
            return TaskStatusUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter options
        view_filter = self.request.query_params.get('filter')
        if view_filter == 'my_tasks' and user.is_authenticated:
            queryset = queryset.filter(assigned_to=user)
        elif view_filter == 'assigned_by_me' and user.is_authenticated:
            queryset = queryset.filter(assigned_by=user)
        
        return queryset

    @permissions_required([PERMISSIONS.CAN_VIEW_TASKS])
    def list(self, request, *args, **kwargs):
        """List all tasks with custom response format."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            message="Tasks retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @permissions_required([PERMISSIONS.CAN_VIEW_TASKS])
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single task with custom response format."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Task retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @permissions_required([PERMISSIONS.CAN_ASSIGN_TASKS])
    def create(self, request, *args, **kwargs):
        """Create a new task with custom response format."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(assigned_by=request.user)
        
        # Return full task details
        task = Task.objects.select_related('assigned_to', 'assigned_by').get(pk=serializer.instance.pk)
        response_serializer = TaskSerializer(task)
        
        return Response(
            success=True,
            message="Task created successfully",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    @permissions_required([PERMISSIONS.CAN_ASSIGN_TASKS])
    def update(self, request, *args, **kwargs):
        """
        Update a task with custom response format.
        - Admin: Can update all fields
        - Non-admin: Can only update status
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        user = request.user
        is_admin = user.is_authenticated and (user.is_admin or user.is_superuser or user.is_staff)
        
        # If non-admin trying to update fields other than status
        if not is_admin:
            allowed_fields = {'status'}
            submitted_fields = set(request.data.keys())
            disallowed_fields = submitted_fields - allowed_fields
            
            if disallowed_fields:
                return Response(
                    success=False,
                    message=f"You can only update the 'status' field. Admin access required for: {', '.join(disallowed_fields)}",
                    status_code=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        
        # Return full task details
        instance.refresh_from_db()
        response_serializer = TaskSerializer(instance)
        
        return Response(
            success=True,
            message="Task updated successfully",
            data=response_serializer.data,
            status_code=status.HTTP_200_OK
        )

    @permissions_required([PERMISSIONS.CAN_ASSIGN_TASKS])
    def destroy(self, request, *args, **kwargs):
        """Delete a task - Admin only."""
        user = request.user
        is_admin = user.is_authenticated and (user.is_admin or user.is_superuser or user.is_staff)
        
        if not is_admin:
            return Response(
                success=False,
                message="Only admins can delete tasks",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        instance = self.get_object()
        instance.delete()
        return Response(
            success=True,
            message="Task deleted successfully",
            status_code=status.HTTP_200_OK
        )
