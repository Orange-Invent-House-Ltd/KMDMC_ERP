from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from dashboard.models import Correspondence


class CorrespondenceSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Correspondence
        fields = [
            'id', 'title', 'description', 'sender', 
            'correspondence_type', 'status', 'action_required', 
            'created_at', 'updated_at', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d ago" if days > 1 else "Yesterday"
        else:
            return obj.created_at.strftime("%b %d, %Y")
