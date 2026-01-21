from rest_framework import serializers
from django.contrib.auth import get_user_model
from correspondence.models import Document

User = get_user_model()


class DocumentUserSerializer(serializers.ModelSerializer):
    """Nested user serializer for documents."""
    initials = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'initials']

    def get_initials(self, obj):
        if obj.name:
            parts = obj.name.split()
            return ''.join([p[0].upper() for p in parts[:2]])
        return obj.email[0].upper() if obj.email else 'U'


class DocumentSerializer(serializers.ModelSerializer):
    """Full serializer for Document model."""
    uploaded_by = DocumentUserSerializer(read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'correspondence', 'title', 'document_type', 'document_type_display',
            'file', 'file_url', 'file_name', 'file_size', 'file_size_formatted',
            'mime_type', 'description', 'uploaded_by', 'created_at'
        ]
        read_only_fields = ['id', 'file_url', 'uploaded_by', 'created_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_size_formatted(self, obj):
        size = obj.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for document lists."""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'document_type_display',
            'file_name', 'file_size', 'file_size_formatted', 'mime_type', 'created_at'
        ]

    def get_file_size_formatted(self, obj):
        size = obj.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/uploading documents."""

    class Meta:
        model = Document
        fields = [
            'correspondence', 'title', 'document_type', 'file', 'description'
        ]

    def create(self, validated_data):
        file = validated_data.get('file')
        if file:
            validated_data['file_name'] = file.name
            validated_data['file_size'] = file.size
            validated_data['mime_type'] = file.content_type
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
