from rest_framework import serializers
from django.utils import timezone
from tasks.models import Task
from user.serializers.user import UserMinimalSerializer


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer for reading and admin updates."""
    assigned_to_details = UserMinimalSerializer(source='assigned_to', read_only=True)
    assigned_by_details = UserMinimalSerializer(source='assigned_by', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'assigned_to_details',
            'assigned_by_details',
            'priority',
            'status',
            'deadline',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks."""
    assigned_to = serializers.CharField(source='assigned_to.name', read_only=True)
    assigned_by = serializers.CharField(source='assigned_by.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'assigned_to',
            'assigned_by',
            'priority',
            'status',
            'deadline',
        ]
        read_only_fields = ['id']

    def validate_deadline(self, value):
        """Ensure deadline is not in the past."""
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def validate_assigned_to(self, value):
        """Ensure task is not assigned to the creator."""
        request = self.context.get('request')
        if request and request.user == value:
            raise serializers.ValidationError("You cannot assign a task to yourself.")
        if not value.is_active:
            raise serializers.ValidationError("Assigned user is not active.")
        return value


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for non-admin users - only status can be updated."""

    class Meta:
        model = Task
        fields = [
                    'id',
                    'title',
                    'description',
                    'assigned_to',
                    'priority',
                    'status',
                    'deadline',
                ]
        read_only_fields = ['id']


class TaskAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin users - all fields can be updated."""

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'assigned_to',
            'priority',
            'status',
            'deadline',
        ]
        read_only_fields = ['id']


class TaskSummarySerializer(serializers.Serializer):
    total_tasks = serializers.SerializerMethodField()
    pending_tasks = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()

    def get_total_tasks(self, obj):
        return obj.count() if hasattr(obj, 'count') else len(obj)

    def get_pending_tasks(self, obj):
        return obj.filter(status='pending').count()

    def get_completed_tasks(self, obj):
        return obj.filter(status='completed').count()

    def get_completion_rate(self, obj):
        total = self.get_total_tasks(obj)
        completed = self.get_completed_tasks(obj)
        return round((completed / total) * 100, 2) if total else 0.0
