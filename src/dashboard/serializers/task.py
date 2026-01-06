from rest_framework import serializers
from django.contrib.auth import get_user_model

from dashboard.models import Task, Department
from .department import DepartmentSerializer
from .user_nested import RequesterSerializer

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = RequesterSerializer(read_only=True)
    assigned_by = RequesterSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True
    )
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_to_id',
            'assigned_by', 'department', 'department_id', 'priority', 
            'status', 'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)
