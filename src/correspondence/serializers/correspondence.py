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

class CorrespondenceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (table display)."""
    is_overdue = serializers.SerializerMethodField()
    parent_id = serializers.ReadOnlyField(source='parent.id')
    reply_count = serializers.IntegerField(source='replies.count', read_only=True)
    receiver = serializers.CharField(source='receiver.name', read_only=True)
    receiver_mail = serializers.CharField(source='receiver.email', read_only=True)
    through = serializers.CharField(source='through.name', read_only=True)
    through_mail = serializers.CharField(source='through.email', read_only=True)
    sender = serializers.CharField(source='sender.name', read_only=True)
    sender_mail = serializers.CharField(source='sender.email', read_only=True)

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
            'receiver_mail',
            'reference_number',
            'through',
            "through_mail",
            'category',
            'is_confidential',
            'note',
            'external_sender',
            'is_overdue',
            'created_at',
            'archived_at',
            "sender",
            "sender_mail",
            "image_urls"
        ]

    def get_is_overdue(self, obj):
        if obj.due_date:
            return timezone.now().date() > obj.due_date
        return False
    
class CorrespondenceRetrieveSerializer(serializers.ModelSerializer):
    """Detailed serializer for retrieving a single correspondence."""
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    receiver_name = serializers.CharField(source='receiver.name', read_only=True)
    receiver_email = serializers.CharField(source='receiver.email', read_only=True)
    through = serializers.CharField(source='through.name', read_only=True)
    through_email = serializers.CharField(source='through.email', read_only=True)
    reply_notes = serializers.SerializerMethodField()
    forwarded_notes = serializers.SerializerMethodField()

    class Meta:
        model = Correspondence
        fields = [ "id", "subject", "parent", "type", "note", "reference_number", "external_sender", "sender_name", "sender_email",
                   "receiver_name", "receiver_email", "through", "through_email",
            'status', 'priority',
            'requires_action', "reply_notes", "forwarded_notes"]

    def get_reply_notes(self, obj):
        return [{"sender": reply.sender.name, 
                 "receiver": reply.receiver.name,
                 "sender_email": reply.sender.email,
                 "receiver_email": reply.receiver.email,
                 "note": reply.note} for reply in obj.replies.filter(status='replied').all()]

    def get_forwarded_notes(self, obj):
        return [{"sender": forward.sender.name,
                 "receiver": forward.receiver.name,
                 "sender_email": forward.sender.email,
                 "receiver_email": forward.receiver.email,
                 "note": forward.note} for forward in obj.replies.filter(status='forwarded').all()]

class CorrespondenceCreateSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Correspondence.objects.all(), 
        required=False, 
        allow_null=True
    )
    receiver_name = serializers.CharField(source='receiver.name', read_only=True)
    receiver_mail = serializers.CharField(source='receiver.email', read_only=True)
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    sender_mail = serializers.CharField(source='sender.email', read_only=True)
    reference_number = serializers.CharField(read_only=True)
    image_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False
    )
    through_name = serializers.CharField(source='through.name', read_only=True)
    through_mail = serializers.CharField(source='through.email', read_only=True)

    class Meta:
        model = Correspondence
        fields = [
            "id",
            'subject',
            'parent',
            'status', 'priority', 'requires_action',
            'due_date',
            "receiver",
            'receiver_name',
            'receiver_mail',
            'sender_name',
            'sender_mail',
            'reference_number',
            'through',
            'through_name',
            'through_mail',
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
        status = validated_data.get('status')
        parent = validated_data.get('parent')
        if parent:
            validated_data['requires_action'] = False
            if validated_data['status'] == 'forwarded':
                if not validated_data['subject'].startswith('Fwd:'):
                    validated_data['subject'] = f"Fwd: {parent.subject}"
                if not validated_data.get('category'):
                    validated_data['category'] = parent.category
            elif validated_data['status'] == 'replied':
                if not validated_data['subject'].startswith('Re:'):
                    validated_data['subject'] = f"Re: {parent.subject}"
                if not validated_data.get('category'):
                    validated_data['category'] = parent.category
        if validated_data.get('status') == 'draft':
            validated_data['status'] = 'draft'
        elif not validated_data.get('requires_action') or validated_data.get('requires_action') is False:
            validated_data["due_date"] = None
            validated_data['status'] = status
        else:
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
