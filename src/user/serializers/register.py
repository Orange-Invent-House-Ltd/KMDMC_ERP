from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from user.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, help_text="User's full name")
    email = serializers.EmailField(help_text="User's email address")
    phone = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="User's phone number (optional)"
    )
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="User's password"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Confirm password"
    )

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "password",
            "confirm_password",
            "is_verified",
            "created_at",
        ]
        read_only_fields = ["id", "is_verified", "created_at"]

    def validate_email(self, value):
        email = value.lower().strip()
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return email

    def validate_phone(self, value):
        if value:
            phone = value.strip()
            if CustomUser.objects.filter(phone=phone).exists():
                raise serializers.ValidationError(
                    "A user with this phone number already exists."
                )
            return phone
        return None

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        return user
