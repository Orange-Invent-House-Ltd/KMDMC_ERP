from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from correspondence.models import Correspondence

User = get_user_model()


class CorrespondenceUserSerializer(serializers.ModelSerializer):
    """Nested user serializer for correspondence."""
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

# ============================================================================
# Main Correspondence Serializers
# ============================================================================


class CorrespondenceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (table display)."""
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Correspondence
        fields = [
            'subject',
            'status', 'priority', 'requires_action',
            'due_date',
            'receiver',
            'reference_number',
            'through',
            'category',
            'is_confidential',
            'note',
            'external_sender',
            'is_overdue',
        ]

    def get_is_overdue(self, obj):
        if obj.due_date:
            return timezone.now().date() > obj.due_date
        return False


class CorrespondenceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new correspondence."""
    reference_number = serializers.CharField(read_only=True)

    class Meta:
        model = Correspondence
        fields = [
            'subject',
            'status', 'priority', 'requires_action',
            'due_date',
            'receiver',
            'reference_number',
            'through',
            'category',
            'is_confidential',
            'note',
            'external_sender',
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs.get('receiver') == user:
            raise serializers.ValidationError("You cannot assign correspondence to yourself.")
        if attrs.get('due_date') and attrs['due_date'] < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['sender'] = user
        if not validated_data.get('requires_action') or validated_data.get('requires_action') is False:
            validated_data["due_date"] = None
            validated_data['status'] = "new"
        else :
            validated_data['status'] = 'pending_action'
        correspondence = super().create(validated_data)
        return correspondence



class CorrespondenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating correspondence."""
    class Meta:
        model = Correspondence
        fields = [
            'subject',
            'status', 'priority', 'requires_action',
            'due_date',
            'receiver',
        ]

    def update(self, instance, validated_data):
        user = self.context['request'].user
        old_receiver = instance.receiver

        # Check if assignment is changing
        new_receiver = validated_data.get('receiver')
        if new_receiver and new_receiver != old_receiver:
            validated_data['assigned_at'] = timezone.now()
        
        correspondence = super().update(instance, validated_data) 
        return correspondence

class CorrespondenceStatusSerializer(serializers.Serializer):
    """Serializer for changing correspondence status."""
    status = serializers.ChoiceField(choices=Correspondence.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class CorrespondenceStatsSerializer(serializers.Serializer):
    """Serializer for correspondence statistics."""
    total = serializers.IntegerField()
    incoming = serializers.IntegerField()
    outgoing = serializers.IntegerField()
    pending_action = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    overdue = serializers.IntegerField()
    by_status = serializers.DictField()
    by_category = serializers.ListField()
    by_priority = serializers.DictField()
    recent_trend = serializers.ListField()
