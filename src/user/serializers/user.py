from rest_framework import serializers

from user.models.models import CustomUser
from user.models.admin import PermissionModule, Permission
from utils.utils import ADMIN_SIDEBAR_MODULES
from user.serializers.permissions import PermissionMinimalSerializer
from tasks.models import Task




class UserMinimalSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)
    permissions = PermissionMinimalSerializer(many=True, source="role.permissions", read_only=True)
    department = serializers.CharField(source="department.name", read_only=True)
    allowed_modules = serializers.SerializerMethodField()
    sidebar_modules = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "name", "sidebar_modules", "allowed_modules", "role", "permissions", "department", "email"]

    def get_permissions(self, obj):
        if obj.role:
            return list(obj.role.permissions.values_list("name", "", flat=True))
        return []

    def get_allowed_modules(self, obj):
        modules = set()
        for permission in obj.role.permissions.all():
            modules.add(permission.module)
        return list(modules.intersection(set(PermissionModule.values())))
    
    def get_sidebar_modules(self, obj):
        modules = set()
        for permission in obj.role.permissions.all():
            modules.add(permission.module)
        return list(modules.union(set(ADMIN_SIDEBAR_MODULES)))


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user details (admin use)."""

    class Meta:
        model = CustomUser
        fields = [
            "is_verified",
        ]
        read_only_fields = ["id"]

class PerformanceOverviewSerializer(serializers.Serializer):
    """Serializer for performance overview data."""
    name = serializers.CharField(source="user.name", read_only=True)
    department = serializers.CharField(source="user.department.name", read_only=True)
    active_tasks = serializers.SerializerMethodField()
    avg_response_time_hours = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    over_due_tasks = serializers.SerializerMethodField(read_only=True)

    def get_active_tasks(self, obj):
        return Task.objects.filter(
            assigned_to=obj.user,
            status__in=['pending', 'in_progress']
        ).count()

    def get_over_due_tasks(self, obj):
        return Task.objects.filter(
            assigned_to=obj.user,
            status='overdue'
        ).count()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout request."""
    refresh = serializers.CharField(
        required=False,
        help_text="Refresh token to blacklist"
    )