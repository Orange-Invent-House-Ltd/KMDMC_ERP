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
from utils.activity_log import extract_api_request_metadata
from audit.tasks import log_audit_event_task
from audit.enums import AuditModuleEnum, AuditStatusEnum, AuditTypeEnum, LogParams
from user.models.models import PerformanceRecord

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
        performance = PerformanceRecord.objects.get_or_create(user=serializer.validated_data['assigned_to'])[0]
        performance.tasks_assigned += 1
        performance.save()

        # Return full task details
        task = Task.objects.select_related('assigned_to', 'assigned_by').get(pk=serializer.instance.pk)
        response_serializer = TaskSerializer(task)
        user = request.user
        event = LogParams(
            audit_type=AuditTypeEnum.CREATE_TASK.raw_value,
            audit_module=AuditModuleEnum.TASKS.raw_value,
            status=AuditStatusEnum.SUCCESS.raw_value,
            user_id=str(user.id),
            user_name=user.name.upper(),
            user_email=user.email,
            user_role=user.role.name,
            action=f"{user.name.upper()} created a task",
            request_meta=extract_api_request_metadata(request),
        )
        log_audit_event_task.delay(event.__dict__)
        return Response(
            success=True,
            message="Task created successfully",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    @permissions_required([PERMISSIONS.CAN_UPDATE_TASK])
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_values = TaskSerializer(instance).data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        if serializer.validated_data.get('status') == 'completed':
            performance = PerformanceRecord.objects.get_or_create(user=instance.assigned_to)[0]
            performance.tasks_completed += 1
            performance.save()
        
        # Return full task details
        instance.refresh_from_db()
        response_serializer = TaskSerializer(instance)
        user = request.user
        event = LogParams(
            audit_type=AuditTypeEnum.UPDATE_TASK.raw_value,
            audit_module=AuditModuleEnum.TASKS.raw_value,
            status=AuditStatusEnum.SUCCESS.raw_value,
            user_id=str(user.id),
            user_name=user.name.upper(),
            user_email=user.email,
            user_role=user.role.name,
            old_values=old_values,
            new_values=serializer.validated_data,
            action=f"{user.name.upper()} updated a task",
            request_meta=extract_api_request_metadata(request),
        )
        log_audit_event_task.delay(event.__dict__)
        return Response(
            success=True,
            message="Task updated successfully",
            data=response_serializer.data,
            status_code=status.HTTP_200_OK
        )

    @permissions_required([PERMISSIONS.CAN_ASSIGN_TASKS])
    def destroy(self, request, *args, **kwargs):
        
        instance = self.get_object()
        instance.delete()
        event = LogParams(
            audit_type=AuditTypeEnum.DELETE_TASK.raw_value,
            audit_module=AuditModuleEnum.TASKS.raw_value,
            status=AuditStatusEnum.SUCCESS.raw_value,
            user_id=str(user.id),
            user_name=request.user.name.upper(),
            user_email=request.user.email,
            user_role=request.user.role.name,
            action=f"{request.user.name.upper()} deleted a task",
            request_meta=extract_api_request_metadata(request),
        )
        log_audit_event_task.delay(event.__dict__)
        return Response(
            success=True,
            message="Task deleted successfully",
            status_code=status.HTTP_200_OK
        )
