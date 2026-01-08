from rest_framework import serializers
from django.contrib.auth import get_user_model
from correspondence.models import CorrespondenceTemplate, Category

User = get_user_model()


class TemplateCreatorSerializer(serializers.ModelSerializer):
    """Nested user serializer for templates."""

    class Meta:
        model = User
        fields = ['id', 'name', 'email']


class TemplateCategorySerializer(serializers.ModelSerializer):
    """Nested category serializer for templates."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'color']


class CorrespondenceTemplateSerializer(serializers.ModelSerializer):
    """Full serializer for CorrespondenceTemplate model."""
    created_by = TemplateCreatorSerializer(read_only=True)
    category = TemplateCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = CorrespondenceTemplate
        fields = [
            'id', 'name', 'description', 'subject_template', 'body_template',
            'category', 'category_id', 'is_active', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class CorrespondenceTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for template lists."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CorrespondenceTemplate
        fields = [
            'id', 'name', 'description', 'subject_template',
            'category_name', 'is_active', 'created_at'
        ]


class CorrespondenceTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating templates."""

    class Meta:
        model = CorrespondenceTemplate
        fields = [
            'name', 'description', 'subject_template', 'body_template',
            'category', 'is_active'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
