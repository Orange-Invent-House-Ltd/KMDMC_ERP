from rest_framework import serializers

from utils.utils import ADMIN_SIDEBAR_MODULES
from user.models.admin import Permission, Role


class PermissionSerializer(serializers.ModelSerializer):
    description = serializers.CharField()

    class Meta:
        model = Permission
        fields = ["id", "name", "description", "module", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class PermissionMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "module"]


class RoleSerializer(serializers.ModelSerializer):
    
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, required=False, write_only=True
    )
    permission_details = PermissionMinimalSerializer(
        source="permissions", many=True, read_only=True
    )
    create_once = serializers.BooleanField(write_only=True, required=False, default=False)
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    allowed_modules = serializers.SerializerMethodField()
    sidebar_modules = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "code",
            "create_once",
            "description",
            "allowed_modules",
            "sidebar_modules",
            "permissions",
            "permission_details",
            "parent",
            "parent_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "allowed_modules",
            "sidebar_modules",
            "permission_details",
            "parent_name",
        ]

    def validate(self, attrs):
            if self.instance and self.instance.create_once:
                if "name" in attrs and attrs["name"] != self.instance.name:
                    raise serializers.ValidationError(
                        {"name": "This role cannot be renamed."}
                    )
                if "code" in attrs and attrs["code"] != self.instance.code:
                    raise serializers.ValidationError(
                        {"code": "This role cannot be recoded."}
                    )
                return super().validate(attrs)

    def get_allowed_modules(self, obj):
        modules = set()
        for permission in obj.permissions.all():
            modules.add(permission.module)
        return list(modules)

    def get_sidebar_modules(self, obj):
        modules = set()
        for permission in obj.permissions.all():
            modules.add(permission.module)
        return list(modules.union(set(ADMIN_SIDEBAR_MODULES)))


class RoleMinimalSerializer(serializers.ModelSerializer):
    permissions = PermissionMinimalSerializer(many=True, read_only=True)
    allowed_modules = serializers.SerializerMethodField()
    sidebar_modules = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "name",
            "code",
            "description",
            "sidebar_modules",
            "allowed_modules",
            "permissions",
        ]

    def get_allowed_modules(self, obj):
        modules = set()
        for permission in obj.permissions.all():
            modules.add(permission.module)
        return list(modules)

    def get_sidebar_modules(self, obj):
        modules = set()
        for permission in obj.permissions.all():
            modules.add(permission.module)
        return list(modules.intersection(set(ADMIN_SIDEBAR_MODULES)))
