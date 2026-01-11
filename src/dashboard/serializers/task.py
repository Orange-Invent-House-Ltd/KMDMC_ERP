from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()


class TaskAssignSerializer(serializers.Serializer):
    """Serializer for reassigning tasks."""
    assigned_to_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_assigned_to_id(self, value):
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("User not found or inactive.")
        return value
