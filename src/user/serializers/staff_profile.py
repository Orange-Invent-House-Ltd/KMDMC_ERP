from rest_framework import serializers
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from user.models import (CustomUser, Department, StaffActivity,
                         PerformanceRecord, StaffTask)
from correspondence.models import Correspondence


# class DepartmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Department
#         fields = ['id', 'name', 'code', 'description', 'is_active']
#         ref_name = 'UserDepartmentSerializer'
    
#     def create(self, validated_data):
#         department = Department.objects.create(**validated_data)
#         return department

class StaffTaskSerializer(serializers.ModelSerializer):
    """Serializer for staff tasks."""
    class Meta:
        model = StaffTask
        fields = [
            'id', 'title', 'description', 'assigned_by',
            'status', 'priority', 'due_date'
        ]

class StaffActivitySerializer(serializers.ModelSerializer):
    """Serializer for staff activity (heatmap data)."""
    activity_level = serializers.ReadOnlyField()

    class Meta:
        model = StaffActivity
        fields = [
            'date', 'activity_count', 'tasks_completed', 'approvals_given',
            'correspondence_handled', 'memos_processed', 'activity_level'
        ]

class StaffCorrespondenceSerializer(serializers.ModelSerializer):
    """Serializer for staff correspondences."""
    class Meta:
        model = Correspondence
        fields = [
            'id', 'subject', 'status', 'priority', 'due_date', 'assigned_to'
        ]

class PerformanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for performance records."""
    month_display = serializers.SerializerMethodField()
    completion_rate = serializers.ReadOnlyField()
    on_time_rate = serializers.ReadOnlyField()

    class Meta:
        model = PerformanceRecord
        fields = [
            'id', 'month', 'month_display',
            'tasks_assigned', 'tasks_completed', 'tasks_on_time',
            'approvals_pending', 'approvals_given', 'avg_approval_time_hours',
            'correspondence_sent', 'correspondence_received', 'avg_response_time_hours',
            'performance_score', 'points_earned',
            'department_rank', 'overall_rank',
            'completion_rate', 'on_time_rate'
        ]

    def get_month_display(self, obj):
        return obj.month.strftime('%B %Y')


class StaffListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for staff directory listing."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    location_display = serializers.CharField(source='get_location_display', read_only=True)
    initials = serializers.ReadOnlyField()
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'name', 'email', 'employee_id', 'position',
            'department_name', 'location', 'location_display',
            'role', 'role_display', 'initials', 'profile_photo_url',
            'is_active'
        ]

    def get_profile_photo_url(self, obj):
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None

class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for basic staff profile details."""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "name",
            "position",
            "department_name",
            "employee_id",
            "location",
            "date_joined_org",
        ]


class StaffProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating staff profile."""
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        required=False,
        allow_null=True
    )
    reports_to_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='reports_to',
        required=False,
        allow_null=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'name', 'phone', 'position', 'department_id', 'location',
            'date_joined_org', 'profile_photo', 'bio',
            'office_phone', 'office_extension', 'reports_to_id'
        ]
