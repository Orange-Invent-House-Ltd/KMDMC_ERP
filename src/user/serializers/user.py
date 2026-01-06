from rest_framework import serializers

from user.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "date_of_birth",
            "is_verified",
            "is_buyer",
            "is_seller",
            "is_admin",
            "is_merchant",
            "kyc_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_verified",
            "is_buyer",
            "is_seller",
            "is_admin",
            "is_merchant",
            "kyc_completed",
            "created_at",
            "updated_at",
        ]


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "name",
            "email",
            "is_verified",
            "is_admin",
        ]
        read_only_fields = fields
