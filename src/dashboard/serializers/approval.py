from rest_framework import serializers
from django.contrib.auth import get_user_model

from dashboard.models import Approval, Department
from .department import DepartmentSerializer
from .user_nested import RequesterSerializer

User = get_user_model()


class ApprovalSerializer(serializers.ModelSerializer):
    requester = RequesterSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    requester_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='requester',
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
        model = Approval
        fields = [
            'id', 'subject', 'description', 'requester', 'requester_id',
            'department', 'department_id', 'urgency', 'status', 'date', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date', 'created_at', 'updated_at']
