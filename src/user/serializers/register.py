from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from user.models.models import CustomUser, Department
from user.models.admin import Role


class RegisterSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
        help_text="User's department ID"
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

    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "role",
            "department",
            "password",
            "confirm_password",
            "is_verified",
            "created_at",
        ]
        read_only_fields = ["id", "email", "is_verified", "created_at"]

    def validate_email(self, value):
        email = value.lower().strip()
        if CustomUser.objects.filter(email__iexact=email).exists():
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
        validated_data["email"] = user.generate_email()
        user.is_active = False
        user.set_password(password)
        user.save()
        user.employee_id = f"KMD-{user.id}"
        user.save(update_fields=["employee_id"])
        return user
