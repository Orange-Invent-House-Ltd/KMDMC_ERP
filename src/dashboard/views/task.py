from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from tasks.models import Task
from django.utils import timezone
from dashboard.serializers import TaskAssignSerializer


class TaskViewSet(viewsets.ModelViewSet):
    
    queryset = Task.objects.select_related(
        'assigned_to', 'assigned_by', 'department'
    ).all()
    serializer_class = TaskAssignSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'priority', 'department', 'assigned_to']
    search_fields = ['title', 'description', 'assigned_to__name']
    ordering_fields = ['created_at', 'deadline', 'priority']

    def get_queryset(self):            
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
        
        serializer = self.get_serializer(data=request.data)
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