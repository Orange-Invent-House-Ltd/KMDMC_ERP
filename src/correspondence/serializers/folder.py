from rest_framework import serializers
from django.contrib.auth import get_user_model
from correspondence.models import CorrespondenceFolder, CorrespondenceFolderItem

User = get_user_model()


class FolderOwnerSerializer(serializers.ModelSerializer):
    """Nested user serializer for folders."""

    class Meta:
        model = User
        fields = ['id', 'name', 'email']


class CorrespondenceFolderSerializer(serializers.ModelSerializer):
    """Full serializer for CorrespondenceFolder model."""
    owner = FolderOwnerSerializer(read_only=True)
    folder_type_display = serializers.CharField(source='get_folder_type_display', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = CorrespondenceFolder
        fields = [
            'id', 'name', 'folder_type', 'folder_type_display', 'description',
            'owner', 'is_system', 'icon', 'color', 'item_count', 'created_at'
        ]
        read_only_fields = ['id', 'owner', 'is_system', 'created_at']

    def get_item_count(self, obj):
        return obj.items.count() if hasattr(obj, 'items') else 0


class CorrespondenceFolderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for folder lists."""
    folder_type_display = serializers.CharField(source='get_folder_type_display', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = CorrespondenceFolder
        fields = [
            'id', 'name', 'folder_type', 'folder_type_display',
            'icon', 'color', 'is_system', 'item_count'
        ]

    def get_item_count(self, obj):
        return obj.items.count() if hasattr(obj, 'items') else 0


class CorrespondenceFolderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating folders."""

    class Meta:
        model = CorrespondenceFolder
        fields = ['name', 'folder_type', 'description', 'icon', 'color']

    def validate_name(self, value):
        user = self.context['request'].user
        if CorrespondenceFolder.objects.filter(name=value, owner=user).exists():
            instance = self.instance
            if not instance or instance.name != value:
                raise serializers.ValidationError("You already have a folder with this name.")
        return value

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        validated_data['is_system'] = False
        return super().create(validated_data)


class CorrespondenceFolderItemSerializer(serializers.ModelSerializer):
    """Serializer for folder items."""
    correspondence_reference = serializers.CharField(
        source='correspondence.reference_number', read_only=True
    )
    correspondence_subject = serializers.CharField(
        source='correspondence.subject', read_only=True
    )

    class Meta:
        model = CorrespondenceFolderItem
        fields = [
            'id', 'folder', 'correspondence', 
            'correspondence_reference', 'correspondence_subject', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']


class AddToFolderSerializer(serializers.Serializer):
    """Serializer for adding correspondence to a folder."""
    correspondence_id = serializers.IntegerField()

    def validate_correspondence_id(self, value):
        from correspondence.models import Correspondence
        if not Correspondence.objects.filter(id=value).exists():
            raise serializers.ValidationError("Correspondence not found.")
        return value
