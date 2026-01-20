from rest_framework import serializers
from correspondence.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    correspondence_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'code', 'description', 'color',
            'is_active', 'correspondence_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_correspondence_count(self, obj):
        return obj.correspondences.count() if hasattr(obj, 'correspondences') else 0


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dropdowns and list views."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'color', 'is_active']


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating categories."""

    class Meta:
        model = Category
        fields = ['name', 'code', 'description', 'color', 'is_active']

    def validate_code(self, value):
        value = value.upper()
        if Category.objects.filter(code=value).exists():
            instance = self.instance
            if not instance or instance.code != value:
                raise serializers.ValidationError("A category with this code already exists.")
        return value
