from rest_framework import serializers

from user.models import CustomUser


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
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

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
