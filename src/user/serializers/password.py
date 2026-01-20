from rest_framework import serializers

from user.models.models import CustomUser
from core.resources.cache import Cache


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="Email address associated with the account"
    )

    def validate_email(self, value):
        email = value.lower().strip()
        if not CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "No account found with this email address."
            )
        return email

    def validate(self, data):
        user = CustomUser.objects.filter(email=data["email"]).first()
        if not user:
            raise serializers.ValidationError(
                "No account found with this email address."
            )
        data["user"] = user
        return data


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(
        help_text="Password reset token"
    )
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="New password"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Confirm new password"
    )

    def validate(self, attrs):
        data = self.get_initial()
        token = data.get("token")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        with Cache() as cache:
            cache_data = cache.get(token)
        if not cache_data or not cache_data.get("is_valid", False):
            raise serializers.ValidationError(
                {"token": "Password reset token is invalid or expired."}
            )
        try:
            user = CustomUser.objects.get(email=cache_data["email"])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"token": "User not found."})

        if user.check_password(password):
            raise serializers.ValidationError(
                {"password": "New password cannot be the same as the old password."}
            )

        with Cache() as cache:
            cache.delete(token)

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Current password"
    )
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="New password"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Confirm new password"
    )

    def validate(self, attrs):
        user = self.context.get("request").user
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if not user.check_password(current_password):
            raise serializers.ValidationError(
                {"current_password": "Current password is incorrect."}
            )

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs
