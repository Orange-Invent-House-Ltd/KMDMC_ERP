from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from dashboard.models import Task
from dashboard.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related(
        'assigned_to', 'assigned_by', 'department'
    ).all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'priority', 'department', 'assigned_to']
    search_fields = ['title', 'description', 'assigned_to__name']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset

    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get all urgent and high priority tasks that are not completed."""
        urgent_tasks = self.get_queryset().filter(
            Q(priority='urgent') | Q(priority='high'),
            status__in=['pending', 'in_progress']
        )
        page = self.paginate_queryset(urgent_tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(urgent_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to the current user."""
        my_tasks = self.get_queryset().filter(assigned_to=request.user)
        page = self.paginate_queryset(my_tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(my_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed."""
        task = self.get_object()
        task.status = 'completed'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
