from rest_framework import serializers
from django.contrib.auth import get_user_model
from correspondence.models import CorrespondenceComment

User = get_user_model()


class CommentAuthorSerializer(serializers.ModelSerializer):
    """Nested user serializer for comments."""
    initials = serializers.SerializerMethodField()
    role_display = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'role_display', 'initials']

    def get_initials(self, obj):
        if obj.name:
            parts = obj.name.split()
            return ''.join([p[0].upper() for p in parts[:2]])
        return obj.email[0].upper() if obj.email else 'U'


class CorrespondenceCommentSerializer(serializers.ModelSerializer):
    """Full serializer for CorrespondenceComment model."""
    author = CommentAuthorSerializer(read_only=True)
    formatted_date = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = CorrespondenceComment
        fields = [
            'id', 'correspondence', 'content', 'is_internal',
            'author', 'created_at', 'updated_at', 'formatted_date', 'time_ago'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_formatted_date(self, obj):
        return obj.created_at.strftime("%b %d, %Y at %H:%M")

    def get_time_ago(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"


class CorrespondenceCommentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for comment lists."""
    author_name = serializers.CharField(source='author.name', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = CorrespondenceComment
        fields = [
            'id', 'content', 'is_internal', 'author_name', 'created_at', 'time_ago'
        ]

    def get_time_ago(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "now"


class CorrespondenceCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""

    class Meta:
        model = CorrespondenceComment
        fields = ['correspondence', 'content', 'is_internal']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
