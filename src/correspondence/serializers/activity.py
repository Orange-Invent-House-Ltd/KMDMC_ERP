from rest_framework import serializers
from django.contrib.auth import get_user_model
from correspondence.models import CorrespondenceActivity

User = get_user_model()


class ActivityUserSerializer(serializers.ModelSerializer):
    """Nested user serializer for activities."""
    initials = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'initials']

    def get_initials(self, obj):
        if obj.name:
            parts = obj.name.split()
            return ''.join([p[0].upper() for p in parts[:2]])
        return obj.email[0].upper() if obj.email else 'U'


class CorrespondenceActivitySerializer(serializers.ModelSerializer):
    """Full serializer for CorrespondenceActivity model."""
    performed_by = ActivityUserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    formatted_timestamp = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = CorrespondenceActivity
        fields = [
            'id', 'correspondence', 'action', 'action_display', 'description',
            'performed_by', 'metadata', 'is_automated',
            'timestamp', 'formatted_timestamp', 'time_ago'
        ]
        read_only_fields = ['id', 'timestamp', 'formatted_timestamp', 'time_ago']

    def get_formatted_timestamp(self, obj):
        return obj.timestamp.strftime("%b %d, %Y at %H:%M")

    def get_time_ago(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.timestamp
        
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


class CorrespondenceActivityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for activity lists."""
    performed_by_name = serializers.CharField(source='performed_by.name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = CorrespondenceActivity
        fields = [
            'id', 'action', 'action_display', 'description',
            'performed_by_name', 'is_automated', 'timestamp', 'time_ago'
        ]

    def get_time_ago(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.timestamp
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "now"


class CorrespondenceActivityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating activities."""

    class Meta:
        model = CorrespondenceActivity
        fields = ['correspondence', 'action', 'description', 'metadata', 'is_automated']

    def create(self, validated_data):
        validated_data['performed_by'] = self.context['request'].user
        return super().create(validated_data)
