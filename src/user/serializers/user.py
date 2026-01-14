from rest_framework import serializers

from user.models.models import CustomUser


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "name"
        ]
        read_only_fields = fields


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