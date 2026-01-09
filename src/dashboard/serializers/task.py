from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from dashboard.models import Task
User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer with nested relationships for read operations."""
    assigned_by = serializers.CharField(read_only = True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    priority = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 
            'assigned_to',
            'assigned_by',
            'priority',
            'status',
            'deadline', 'is_overdue', 'days_until_deadline',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at', 'updated_at']

    def get_is_overdue(self, obj):
        """Check if task is overdue."""
        if obj.deadline and obj.status not in ['completed']:
            return timezone.now().date() > obj.deadline
        return False

    def get_days_until_deadline(self, obj):
        """Calculate days remaining until deadline."""
        if obj.deadline:
            delta = obj.deadline - timezone.now().date()
            return delta.days
        return None

    def validate_deadline(self, value):
        """Ensure deadline is not in the past for new tasks."""
        if value and self.instance is None:  # Only for create
            if value < timezone.now().date():
                raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def create(self, validated_data):
        """Create task and set assigned_by to current user."""
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update task with status change tracking."""
        old_status = instance.status
        task = super().update(instance, validated_data)
        # TODO- send notifications when tasks are completed
        return task


class TaskCreateSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task creation."""
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to'
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to_id', 
            'department_id', 'priority', 'deadline'
        ]

    def validate_deadline(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        task = Task.objects.create(**validated_data)
        return task


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'assigned_to_name', 'assigned_by_name',
            'department_name', 'priority', 'priority_display',
            'status', 'status_display', 'deadline', 'is_overdue', 'created_at'
        ]

    def get_is_overdue(self, obj):
        if obj.deadline and obj.status not in ['completed']:
            return timezone.now().date() > obj.deadline
        return False


class TaskStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating task status."""
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        instance = self.context.get('instance')
        if instance:
            # Prevent reopening completed tasks (optional business rule)
            if instance.status == 'completed' and value != 'completed':
                raise serializers.ValidationError(
                    "Cannot change status of completed tasks. Create a new task instead."
                )
        return value


class TaskAssignSerializer(serializers.Serializer):
    """Serializer for reassigning tasks."""
    assigned_to_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_assigned_to_id(self, value):
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("User not found or inactive.")
        return value
