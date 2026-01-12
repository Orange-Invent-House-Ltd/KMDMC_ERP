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

class CorrespondenceSerializer(serializers.ModelSerializer):
    """Full serializer for Correspondence model with all related data."""
    receiver = serializers.CharField(source='receiver.name', read_only=True)
    sender = serializers.CharField(source='sender.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Correspondence
        fields = [
            'id', 'subject',
            'status', 'status_display', 'priority', 'priority_display',
            'requires_action', 'due_date',
            'receiver', 'sender',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_overdue(self, obj):
        if obj.due_date:
            return timezone.now().date() > obj.due_date
        return False


class CorrespondenceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (table display)."""
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Correspondence
        fields = [
            'id', 'subject',
            'status', 'status_display', 'priority_display',
            'requires_action',
            'due_date',
            'assigned_to_name', 'is_overdue',
            'created_at'
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
        # validated_data['reference_number'] = Correspondence._generate_reference()
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
