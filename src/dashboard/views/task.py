from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from dashboard.models import Task
from dashboard.serializers import (
    TaskSerializer, 
    TaskCreateSerializer,
    TaskListSerializer,
    TaskStatusUpdateSerializer,
    TaskAssignSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    
    Provides CRUD operations plus custom actions for:
    - Listing urgent tasks
    - Getting user's assigned tasks
    - Marking tasks as complete
    - Updating task status
    - Reassigning tasks
    - Getting overdue tasks
    """
    queryset = Task.objects.select_related(
        'assigned_to', 'assigned_by', 'department'
    ).all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'priority', 'department', 'assigned_to']
    search_fields = ['title', 'description', 'assigned_to__name']
    ordering_fields = ['created_at', 'deadline', 'priority']

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()
            
        queryset = super().get_queryset()
        
        status_filter = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        assigned_to = self.request.query_params.get('assigned_to')
        department = self.request.query_params.get('department')
        overdue_only = self.request.query_params.get('overdue')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority:
            queryset = queryset.filter(priority=priority)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        if department:
            queryset = queryset.filter(department_id=department)
        if overdue_only and overdue_only.lower() == 'true':
            queryset = queryset.filter(
                deadline__lt=timezone.now().date(),
                status__in=['pending', 'in_progress']
            )
        
        return queryset

    def perform_create(self, serializer):
        """Set assigned_by to current user when creating a task."""
        serializer.save(assigned_by=self.request.user)

    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get all urgent and high priority tasks that are not completed."""
        urgent_tasks = self.get_queryset().filter(
            Q(priority='high') | Q(priority='urgent'),
            status__in=['pending', 'in_progress']
        ).order_by('deadline', '-priority')
        
        page = self.paginate_queryset(urgent_tasks)
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TaskListSerializer(urgent_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to the current user."""
        my_tasks = self.get_queryset().filter(assigned_to=request.user)
        
        # Additional filtering
        status_filter = request.query_params.get('status')
        if status_filter:
            my_tasks = my_tasks.filter(status=status_filter)
        
        page = self.paginate_queryset(my_tasks)
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TaskListSerializer(my_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def created_by_me(self, request):
        """Get tasks created/assigned by the current user."""
        created_tasks = self.get_queryset().filter(assigned_by=request.user)
        
        page = self.paginate_queryset(created_tasks)
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TaskListSerializer(created_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue tasks."""
        overdue_tasks = self.get_queryset().filter(
            deadline__lt=timezone.now().date(),
            status__in=['pending', 'in_progress']
        ).order_by('deadline')
        
        page = self.paginate_queryset(overdue_tasks)
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TaskListSerializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed."""
        task = self.get_object()
        
        # Only assignee or creator can complete the task
        if task.assigned_to != request.user and task.assigned_by != request.user:
            return Response(
                {'error': 'You do not have permission to complete this task.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if task.status == 'completed':
            return Response(
                {'error': 'Task is already completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'completed'
        task.save()
        
        serializer = TaskSerializer(task, context={'request': request})
        return Response({
            'success': True,
            'message': 'Task marked as completed.',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Mark a task as in progress."""
        task = self.get_object()
        
        if task.status != 'pending':
            return Response(
                {'error': 'Only pending tasks can be started.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'in_progress'
        task.save()
        
        serializer = TaskSerializer(task, context={'request': request})
        return Response({
            'success': True,
            'message': 'Task started.',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update task status with validation."""
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(
            data=request.data,
            context={'request': request, 'instance': task}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = serializer.validated_data['status']
        task.save()
        
        return Response({
            'success': True,
            'message': f'Task status updated to {task.get_status_display()}.',
            'data': TaskSerializer(task, context={'request': request}).data
        })

    @action(detail=True, methods=['post'])
    def reassign(self, request, pk=None):
        """Reassign task to another user."""
        task = self.get_object()
        
        # Only creator or admin can reassign
        if task.assigned_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to reassign this task.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TaskAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        new_assignee = User.objects.get(id=serializer.validated_data['assigned_to_id'])
        old_assignee = task.assigned_to
        
        task.assigned_to = new_assignee
        task.save()
        
        return Response({
            'success': True,
            'message': f'Task reassigned from {old_assignee.name} to {new_assignee.name}.',
            'data': TaskSerializer(task, context={'request': request}).data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get task statistics for the current user."""
        user = request.user
        base_qs = Task.objects.all()
        
        # Tasks assigned to user
        my_tasks = base_qs.filter(assigned_to=user)
        
        # Tasks created by user
        created_tasks = base_qs.filter(assigned_by=user)
        
        stats = {
            'assigned_to_me': {
                'total': my_tasks.count(),
                'pending': my_tasks.filter(status='pending').count(),
                'in_progress': my_tasks.filter(status='in_progress').count(),
                'completed': my_tasks.filter(status='completed').count(),
                'overdue': my_tasks.filter(
                    deadline__lt=timezone.now().date(),
                    status__in=['pending', 'in_progress']
                ).count(),
            },
            'created_by_me': {
                'total': created_tasks.count(),
                'pending': created_tasks.filter(status='pending').count(),
                'in_progress': created_tasks.filter(status='in_progress').count(),
                'completed': created_tasks.filter(status='completed').count(),
            }
        }
        
        return Response(stats)
