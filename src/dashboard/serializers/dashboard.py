from rest_framework import serializers
from .approval import ApprovalSerializer
from .correspondence import CorrespondenceSerializer
from .performance import DepartmentPerformanceSerializer


class DashboardStatsSerializer(serializers.Serializer):
    pending_approvals = serializers.IntegerField()
    pending_approvals_change = serializers.IntegerField()
    urgent_tasks = serializers.IntegerField()
    urgent_tasks_change = serializers.CharField()
    correspondence_count = serializers.IntegerField()
    correspondence_change = serializers.CharField()
    staff_active_percentage = serializers.CharField()
    staff_status = serializers.CharField()


class DashboardSerializer(serializers.Serializer):
    stats = DashboardStatsSerializer()
    pending_approvals = ApprovalSerializer(many=True)
    recent_correspondence = CorrespondenceSerializer(many=True)
    department_performance = DepartmentPerformanceSerializer(many=True)
