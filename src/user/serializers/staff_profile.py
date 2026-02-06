from rest_framework import serializers
from user.models.models import (CustomUser, Department, StaffActivity,
                         PerformanceRecord)
from correspondence.models import Correspondence
from tasks.serializers import TaskSummarySerializer 
from django.contrib.auth import get_user_model

User = get_user_model()

class StaffActivitySerializer(serializers.ModelSerializer):
    """Serializer for staff activity (heatmap data)."""
    activity_level = serializers.ReadOnlyField()

    class Meta:
        model = StaffActivity
        fields = [
            'date', 'activity_count', 'approvals_pending',
            'correspondence_handled', 'memos_processed', 'activity_level'
        ]

class StaffCorrespondenceSerializer(serializers.ModelSerializer):
    """Serializer for staff correspondences."""
    class Meta:
        model = Correspondence
        fields = [
            'id', 'subject', 'status', 'priority', 'due_date'
        ]

class PerformanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for performance records."""
    completion_rate = serializers.ReadOnlyField()
    on_time_rate = serializers.ReadOnlyField()

    class Meta:
        model = PerformanceRecord
        fields = [
            'id',
            'tasks_assigned', 'tasks_completed', 'tasks_on_time',
            'correspondence_sent', 'correspondence_received',
            'performance_score', 'points_earned',
            'completion_rate', 'on_time_rate'
        ]

class StaffListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for staff directory listing."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    location_display = serializers.CharField(source='get_location_display', read_only=True)
    initials = serializers.ReadOnlyField()
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'name', 'email', 'employee_id',
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
    department = serializers.StringRelatedField()
    activity = StaffActivitySerializer(many=True, source='staffactivity_set', read_only=True)
    performance = PerformanceRecordSerializer(many=True, source='performancerecord_set', read_only=True)
    correspondence = StaffCorrespondenceSerializer(many=True, source='correspondence_set', read_only=True)
    task_summary = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', "name", 'email', 'department', "role", "location", 'date_joined', "employee_id",
            'is_active', 'is_staff', 'activity', 'performance', 'correspondence', 'task_summary'
        ]

    def get_task_summary(self, obj):
        from tasks.models import Task
        tasks = Task.objects.filter(assigned_to=obj)
        serializer = TaskSummarySerializer(tasks, context=self.context)
        return serializer.data

    def get_date_joined(self, obj):
        return obj.date_joined.strftime('%B %d, %Y')


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
            'name', 'phone', 'role', 'department_id', 'location',
            'date_joined_org', 'profile_photo', 'bio',
            'office_phone', 'office_extension', 'reports_to_id'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'email': {'required': False},
            'location': {'required': False},
        }

class UserDropdownSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "label", "email"]

    def get_label(self, obj):
        return f"{obj.name}"