from django.contrib.auth import authenticate
from rest_framework import serializers
from .user import UserMinimalSerializer


class LoginSerializer(serializers.Serializer):

    login = serializers.CharField(
        help_text="email address"
    )
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False,
        help_text="User's password"
    )
    remember_me = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Keep user logged in for extended period"
    )

    def validate_login(self, value):
        """Normalize login to lowercase."""
        return value.lower().strip()

    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")

        if login and password:
            user = authenticate(
                request=self.context.get("request"),
                email=login,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    "Invalid email or password.",
                    code="authentication"
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    "This account has been deactivated.",
                    code="authorization"
                )

            attrs["user"] = user

        return attrs


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response."""

    token = serializers.CharField(help_text="Authentication token")
    user = UserMinimalSerializer(help_text="User details")
    message = serializers.CharField(help_text="Response message")
