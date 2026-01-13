from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from memo.models import Memo, MemoApproval, MemoAttachment

User = get_user_model()


class MemoUserSerializer(serializers.ModelSerializer):
    """Nested user serializer for memo participants."""
    initials = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'role_display',
                  'initials', 'department_name']

    def get_initials(self, obj):
        if obj.name:
            parts = obj.name.split()
            return ''.join([p[0].upper() for p in parts[:2]])
        return obj.email[0].upper() if obj.email else 'U'


class MemoAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for memo attachments."""
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)
    file_size_display = serializers.CharField(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MemoAttachment
        fields = [
            'id', 'file_name', 'file_size', 'file_size_display',
            'file_type', 'file_url', 'description',
            'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class MemoApprovalSerializer(serializers.ModelSerializer):
    """Serializer for approval history."""
    actor_name = serializers.CharField(source='actor.name', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = MemoApproval
        fields = [
            'id', 'stage', 'stage_display', 'action', 'action_display',
            'actor_name', 'comments', 'action_date'
        ]
        read_only_fields = ['id', 'action_date']


# ============================================================================
# Main Memo Serializers (following correspondence pattern)
# ============================================================================

class MemoListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (table display)."""
    initiator_name = serializers.CharField(source='initiator.name', read_only=True)
    to_unit_head_name = serializers.CharField(source='to_unit_head.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    attachment_count = serializers.SerializerMethodField()

    class Meta:
        model = Memo
        fields = [
            'id', 'reference_number', 'subject',
            'status', 'status_display', 'priority', 'priority_display',
            'current_stage', 'initiator_name', 'to_unit_head_name',
            'attachment_count', 'is_locked',
            'created_at', 'submitted_at'
        ]

    def get_attachment_count(self, obj):
        return obj.attachments.count()


class MemoDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer with all related data."""
    initiator = MemoUserSerializer(read_only=True)
    to_unit_head = MemoUserSerializer(read_only=True)
    through_cc = MemoUserSerializer(read_only=True)
    final_approver = MemoUserSerializer(read_only=True)

    attachments = MemoAttachmentSerializer(many=True, read_only=True)
    approvals = MemoApprovalSerializer(many=True, read_only=True)

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    can_edit = serializers.BooleanField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)

    class Meta:
        model = Memo
        fields = [
            'id', 'reference_number', 'subject', 'content',
            'priority', 'priority_display',
            'status', 'status_display', 'current_stage',
            'initiator', 'to_unit_head', 'through_cc', 'final_approver',
            'attachments', 'approvals',
            'is_locked', 'can_edit', 'can_cancel',
            'submitted_at', 'reviewed_at', 'approved_at', 'rejected_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reference_number', 'created_at', 'updated_at']


class MemoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new memos."""
    reference_number = serializers.CharField(read_only=True)
    attachment_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Memo
        fields = [
            'subject', 'content', 'priority',
            'to_unit_head', 'through_cc',
            'attachment_files', 'reference_number'
        ]

    def validate(self, attrs):
        """Validate memo creation data."""
        user = self.context['request'].user

        # Cannot assign memo to yourself as Unit Head
        if attrs.get('to_unit_head') == user:
            raise serializers.ValidationError(
                "You cannot assign a memo to yourself as the reviewer."
            )

        # Validate Unit Head role
        to_unit_head = attrs.get('to_unit_head')
        if to_unit_head and to_unit_head.role not in ['director', 'hr_manager', 'super_admin']:
            raise serializers.ValidationError(
                "Unit Head must be a Director, HR Manager, or Super Admin."
            )

        return attrs

    def create(self, validated_data):
        """Create memo with initiator and handle attachments."""
        attachment_files = validated_data.pop('attachment_files', [])
        user = self.context['request'].user

        # Set initiator
        validated_data['initiator'] = user

        # Determine final approver based on organization hierarchy
        # For now, assign to director role
        final_approver = User.objects.filter(role='director').first()
        validated_data['final_approver'] = final_approver

        # Create memo
        memo = super().create(validated_data)

        # Handle attachments
        for file in attachment_files:
            MemoAttachment.objects.create(
                memo=memo,
                file=file,
                file_name=file.name,
                file_size=file.size,
                file_type=file.content_type,
                uploaded_by=user
            )

        return memo


class MemoUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating memos (only allowed in draft status)."""

    class Meta:
        model = Memo
        fields = [
            'subject', 'content', 'priority',
            'to_unit_head', 'through_cc'
        ]

    def validate(self, attrs):
        """Only allow updates if memo is in draft and not locked."""
        memo = self.instance

        if memo.is_locked:
            raise serializers.ValidationError(
                "Cannot edit locked memo. Memo has been submitted for approval."
            )

        if memo.status != 'draft':
            raise serializers.ValidationError(
                f"Cannot edit memo in '{memo.get_status_display()}' status. "
                "Only draft memos can be edited."
            )

        return attrs


class MemoActionSerializer(serializers.Serializer):
    """Serializer for workflow actions (approve, reject, etc.)."""
    action = serializers.ChoiceField(
        choices=['approve', 'reject', 'return'],
        required=True
    )
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )
