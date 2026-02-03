from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from correspondence.models import Correspondence, CorrespondenceDelegate


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

class CorrespondenceThreadSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Correspondence
        fields = '__all__'

    def get_replies(self, obj):
        serializer = CorrespondenceThreadSerializer(obj.replies.all(), many=True)
        return serializer.data

class CorrespondenceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (table display)."""
    is_overdue = serializers.SerializerMethodField()
    parent_id = serializers.ReadOnlyField(source='parent.id')
    reply_count = serializers.IntegerField(source='replies.count', read_only=True)

    class Meta:
        model = Correspondence
        fields = [
            'id',
            'subject', "type",
            'status', 'priority', 'requires_action',
            'parent_id',
            'reply_count',
            'due_date',
            'receiver',
            'reference_number',
            'through',
            'category',
            'is_confidential',
            'note',
            'external_sender',
            'is_overdue',
            'created_at',
            'archived_at',
            "sender",
            "image_urls"
        ]

    def get_is_overdue(self, obj):
        if obj.due_date:
            return timezone.now().date() > obj.due_date
        return False
    
class CorrespondenceRetrieveSerializer(serializers.ModelSerializer):
    """Detailed serializer for retrieving a single correspondence."""

    reply_notes = serializers.SerializerMethodField()

    class Meta:
        model = Correspondence
        fields = ["parent", "reply_notes", "id", "subject", "type",
            'status', 'priority', 'requires_action',]

    def get_reply_notes(self, obj):
        return [{"user": reply.sender.username, "note": reply.note} for reply in obj.replies.all()]

class CorrespondenceCreateSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Correspondence.objects.all(), 
        required=False, 
        allow_null=True
    )
    reference_number = serializers.CharField(read_only=True)
    image_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False
    )
    through = serializers.CharField(source='through.name', read_only=True)

    class Meta:
        model = Correspondence
        fields = [
            'subject',
            'parent',
            'status', 'priority', 'requires_action',
            'due_date',
            'receiver',
            'reference_number',
            'through',
            'category',
            'is_confidential',
            'note',
            'image_urls',
            'external_sender',
            "type",
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
        parent = validated_data.get('parent')
        if parent:
            if not validated_data['subject'].startswith('Re:'):
                validated_data['subject'] = f"Re: {parent.subject}"
            if not validated_data.get('category'):
                validated_data['category'] = parent.category
        if validated_data.get('status') == 'draft':
            validated_data['status'] = 'draft'
        elif not validated_data.get('requires_action') or validated_data.get('requires_action') is False:
            validated_data["due_date"] = None
            validated_data['status'] = "new"
        else:
            validated_data['status'] = 'pending_action'
        correspondence = super().create(validated_data)
        return correspondence

class CorrespondenceThreadSerializer(serializers.ModelSerializer):
    pass
    # replies = serializers.SerializerMethodField()

    # class Meta:
    #     model = Correspondence
    #     fields = '__all__'

    # def get_replies(self, obj):
    #     serializer = CorrespondenceThreadSerializer(obj.replies.all(), many=True)
    #     return serializer.data
    
class CorrespondenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating correspondence."""
    class Meta:
        model = Correspondence
        fields = [
            'subject',
            'status', 'priority', 'requires_action',
            'due_date',
            'receiver',
            'note',
            "type",
            'md_note',
        ]

    def update(self, instance, validated_data):
        user = self.context['request'].user
        old_receiver = instance.receiver

        # Check if assignment is changing
        new_receiver = validated_data.get('receiver')
        if new_receiver and new_receiver != old_receiver:
            validated_data['assigned_at'] = timezone.now()

        #set archive date if status is archived
        if validated_data.get('status') == 'archived':
            validated_data['archived_at'] = timezone.now()
        
        correspondence = super().update(instance, validated_data) 
        return correspondence
    

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

class CorrespondenceDelegateSerializer(serializers.ModelSerializer):
    """Serializer for correspondence delegates."""
    class Meta:
        model = CorrespondenceDelegate
        fields = [
            'id',
            'correspondence',
            'delegated_to',
            'note',
            'delegated_at',
        ]
    
    def validate(self, attrs):
        user = self.context['request'].user
        if attrs.get('delegated_to') == user:
            raise serializers.ValidationError("You cannot delegate correspondence to yourself.")
        return attrs

    def create(self, validated_data):
        CorrespondenceDelegate.objects.filter(
            correspondence=validated_data['correspondence'],
            is_active=True
        ).update(is_active=False)
        validated_data['is_active'] = True
        delegate, _ = CorrespondenceDelegate.objects.update_or_create(
            correspondence=validated_data['correspondence'],
            delegated_to=validated_data['delegated_to'],
            defaults={
                'delegated_by': self.context['request'].user,
                'note': validated_data.get('note', ''),
                'is_active': True
            }
        )
        return delegate
