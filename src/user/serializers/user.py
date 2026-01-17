from rest_framework import serializers

from user.models.models import CustomUser


class UserMinimalSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)
    permissions = serializers.SerializerMethodField()
    department = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "name", "role", "permissions", "department", "email"]

    def get_permissions(self, obj):
        if obj.role:
            return list(obj.role.permissions.values_list("name", flat=True))
        return []


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user details (admin use)."""

    class Meta:
        model = CustomUser
        fields = [
            "is_verified",
        ]
        read_only_fields = ["id"]


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout request."""
    refresh = serializers.CharField(
        required=False,
        help_text="Refresh token to blacklist"
    )