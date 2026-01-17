from rest_framework import serializers
from hr_config.models import LeaveApprovalWorkflow, LeaveApprovalStage


class LeaveApprovalStageSerializer(serializers.ModelSerializer):
    """Serializer for individual approval stages."""
    approver_type_display = serializers.CharField(source='get_approver_type_display', read_only=True)

    class Meta:
        model = LeaveApprovalStage
        fields = [
            'id',
            'stage_order',
            'stage_name',
            'approver_type',
            'approver_type_display',
            'required_role',
            'is_required',
            'can_skip',
        ]


class LeaveApprovalWorkflowListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing workflows."""
    stage_count = serializers.SerializerMethodField()

    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            'id',
            'workflow_name',
            'is_active',
            'enable_auto_approval',
            'auto_approve_threshold_days',
            'stage_count',
            'created_at',
            'updated_at',
        ]

    def get_stage_count(self, obj):
        """Count approval stages."""
        return obj.stages.count()


class LeaveApprovalWorkflowDetailSerializer(serializers.ModelSerializer):
    """Full serializer with stages for detail view."""
    stages = LeaveApprovalStageSerializer(many=True, read_only=True)

    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            'id',
            'workflow_name',
            'is_active',
            'enable_auto_approval',
            'auto_approve_threshold_days',
            'stages',
            'created_at',
            'updated_at',
        ]


class LeaveApprovalStageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating approval stages."""

    class Meta:
        model = LeaveApprovalStage
        fields = [
            'stage_order',
            'stage_name',
            'approver_type',
            'required_role',
            'is_required',
            'can_skip',
        ]


class LeaveApprovalWorkflowCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workflows with stages."""
    stages = LeaveApprovalStageCreateSerializer(many=True)

    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            'workflow_name',
            'is_active',
            'enable_auto_approval',
            'auto_approve_threshold_days',
            'stages',
        ]

    def create(self, validated_data):
        """Create workflow with nested stages."""
        stages_data = validated_data.pop('stages')
        workflow = LeaveApprovalWorkflow.objects.create(**validated_data)

        for stage_data in stages_data:
            LeaveApprovalStage.objects.create(workflow=workflow, **stage_data)

        return workflow


class LeaveApprovalWorkflowUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating workflows."""

    class Meta:
        model = LeaveApprovalWorkflow
        fields = [
            'workflow_name',
            'is_active',
            'enable_auto_approval',
            'auto_approve_threshold_days',
        ]
