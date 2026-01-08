from rest_framework import serializers
from correspondence.models import Classification


class ClassificationSerializer(serializers.ModelSerializer):
    """Serializer for Classification model."""
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = Classification
        fields = [
            'id', 'name', 'level', 'level_display', 'description',
            'color', 'requires_approval', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ClassificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dropdowns."""
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = Classification
        fields = ['id', 'name', 'level', 'level_display', 'color', 'requires_approval']


class ClassificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating classifications."""

    class Meta:
        model = Classification
        fields = ['name', 'level', 'description', 'color', 'requires_approval']

    def validate_level(self, value):
        if Classification.objects.filter(level=value).exists():
            instance = self.instance
            if not instance or instance.level != value:
                raise serializers.ValidationError("A classification with this level already exists.")
        return value
