from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.db import transaction, models
from django.shortcuts import get_object_or_404

from utils.response import Response
from utils.pagination import CustomPagination
from audit.enums import AuditModuleEnum, AuditStatusEnum, AuditTypeEnum, LogParams
from audit.tasks import log_audit_event_task

from memo.models import Memo, MemoApproval, MemoAttachment
from memo.serializers import (
    MemoListSerializer,
    MemoDetailSerializer,
    MemoCreateSerializer,
    MemoUpdateSerializer,
    MemoActionSerializer,
)
from memo.permissions import MemoPermissions


class MemoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing memos with approval workflow.

    Custom Actions:
    - submit_for_approval: Submit draft for review
    - approve: Approve at current stage
    - reject: Reject memo
    - cancel: Cancel draft memo
    """

    queryset = Memo.objects.all().select_related(
        'initiator', 'to_unit_head', 'through_cc', 'final_approver'
    ).prefetch_related('attachments', 'approvals')

    permission_classes = [IsAuthenticated, MemoPermissions]
    pagination_class = CustomPagination
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filterset_fields = ['status', 'priority', 'current_stage', 'initiator', 'to_unit_head']
    search_fields = ['reference_number', 'subject', 'content']
    ordering_fields = ['created_at', 'submitted_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return MemoListSerializer
        elif self.action == 'create':
            return MemoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MemoUpdateSerializer
        elif self.action in ['approve', 'reject']:
            return MemoActionSerializer
        return MemoDetailSerializer

    def get_queryset(self):
        """Filter queryset based on user role."""
        if getattr(self, 'swagger_fake_view', False):
            return Memo.objects.none()

        user = self.request.user

        # Super admin and directors see all
        if user.role in ['super_admin', 'director']:
            return super().get_queryset()

        # HR managers see memos in their department
        if user.role == 'hr_manager':
            return super().get_queryset().filter(
                models.Q(initiator__department=user.department) |
                models.Q(to_unit_head=user) |
                models.Q(through_cc=user) |
                models.Q(final_approver=user)
            )

        # General staff see only their own memos and memos assigned to them
        return super().get_queryset().filter(
            models.Q(initiator=user) |
            models.Q(to_unit_head=user) |
            models.Q(through_cc=user)
        )

    def create(self, request, *args, **kwargs):
        """Create memo directly (auto-saves as draft)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        memo = serializer.save()

        # Log audit
        self._log_audit(
            user=request.user,
            action="Created memo draft",
            memo=memo,
            audit_type=AuditTypeEnum.CREATE_MEMO,
            status=AuditStatusEnum.SUCCESS
        )

        return Response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Memo created successfully as draft",
            data=MemoDetailSerializer(memo, context={'request': request}).data
        )

    def update(self, request, *args, **kwargs):
        """Update memo (only if draft and not locked)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        memo = serializer.save()

        # Log audit
        self._log_audit(
            user=request.user,
            action="Updated memo draft",
            memo=memo,
            audit_type=AuditTypeEnum.EDIT_MEMO,
            status=AuditStatusEnum.SUCCESS
        )

        return Response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Memo updated successfully",
            data=MemoDetailSerializer(memo, context={'request': request}).data
        )

    @action(detail=True, methods=['post'], url_path='submit-for-approval')
    def submit_for_approval(self, request, pk=None):
        """
        Submit memo for approval workflow.
        Transitions: draft -> pending_review
        Locks the memo to prevent further edits.
        """
        memo = self.get_object()

        # Validate memo can be submitted
        if memo.status != 'draft':
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                message=f"Cannot submit memo in '{memo.get_status_display()}' status"
            )

        if memo.is_locked:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                message="Memo is already locked"
            )

        # Validate required fields
        if not memo.to_unit_head:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                message="Unit Head must be assigned before submission"
            )

        with transaction.atomic():
            # Update memo status
            memo.status = 'pending_review'
            memo.current_stage = 2
            memo.is_locked = True
            memo.locked_at = timezone.now()
            memo.submitted_at = timezone.now()
            memo.save()

            # Create approval record
            MemoApproval.objects.create(
                memo=memo,
                stage=1,
                action='submitted',
                actor=request.user,
                comments="Submitted for review"
            )

        # Log audit
        self._log_audit(
            user=request.user,
            action=f"Submitted memo {memo.reference_number} for approval",
            memo=memo,
            audit_type=AuditTypeEnum.SUBMIT_MEMO,
            status=AuditStatusEnum.SUCCESS
        )

        return Response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Memo submitted for approval successfully",
            data=MemoDetailSerializer(memo, context={'request': request}).data
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve memo at current stage.
        Stage 2 (Unit Head): pending_review -> pending_approval
        Stage 3 (Director/MD): pending_approval -> approved
        """
        memo = self.get_object()
        user = request.user

        serializer = MemoActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comments = serializer.validated_data.get('comments', '')

        # Validate user can approve at current stage
        if memo.current_stage == 2 and memo.to_unit_head != user:
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                message="Only the assigned Unit Head can approve at this stage"
            )

        if memo.current_stage == 3 and memo.final_approver != user:
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                message="Only the Director/MD can give final approval"
            )

        with transaction.atomic():
            # Create approval record
            MemoApproval.objects.create(
                memo=memo,
                stage=memo.current_stage,
                action='approved',
                actor=user,
                comments=comments
            )

            # Update memo based on stage
            if memo.current_stage == 2:
                # Unit Head approval -> move to Director/MD
                memo.status = 'pending_approval'
                memo.current_stage = 3
                memo.reviewed_at = timezone.now()
            elif memo.current_stage == 3:
                # Final approval
                memo.status = 'approved'
                memo.approved_at = timezone.now()

            memo.save()

        # Log audit
        self._log_audit(
            user=user,
            action=f"Approved memo {memo.reference_number} at stage {memo.current_stage}",
            memo=memo,
            audit_type=AuditTypeEnum.APPROVE_MEMO,
            status=AuditStatusEnum.SUCCESS
        )

        return Response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Memo approved successfully",
            data=MemoDetailSerializer(memo, context={'request': request}).data
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject memo at any stage."""
        memo = self.get_object()
        user = request.user

        serializer = MemoActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comments = serializer.validated_data.get('comments', '')

        if not comments:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                message="Rejection comments are required"
            )

        # Validate user can reject
        valid_rejectors = [memo.to_unit_head, memo.final_approver]
        if user not in valid_rejectors:
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                message="You do not have permission to reject this memo"
            )

        with transaction.atomic():
            # Create rejection record
            MemoApproval.objects.create(
                memo=memo,
                stage=memo.current_stage,
                action='rejected',
                actor=user,
                comments=comments
            )

            # Update memo
            memo.status = 'rejected'
            memo.rejected_at = timezone.now()
            memo.save()

        # Log audit
        self._log_audit(
            user=user,
            action=f"Rejected memo {memo.reference_number}",
            memo=memo,
            audit_type=AuditTypeEnum.REJECT_MEMO,
            status=AuditStatusEnum.SUCCESS
        )

        return Response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Memo rejected successfully",
            data=MemoDetailSerializer(memo, context={'request': request}).data
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel draft memo (only initiator can cancel)."""
        memo = self.get_object()

        if memo.initiator != request.user:
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                message="Only the initiator can cancel a memo"
            )

        if memo.status != 'draft':
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                message="Only draft memos can be cancelled"
            )

        memo.status = 'cancelled'
        memo.save()

        # Log audit
        self._log_audit(
            user=request.user,
            action=f"Cancelled memo {memo.reference_number}",
            memo=memo,
            audit_type=AuditTypeEnum.CANCEL_MEMO,
            status=AuditStatusEnum.SUCCESS
        )

        return Response(
            status_code=status.HTTP_200_OK,
            success=True,
            message="Memo cancelled successfully"
        )

    def _log_audit(self, user, action, memo, audit_type, status):
        """Helper to log audit events."""
        log_params = LogParams(
            audit_module=AuditModuleEnum.MEMO,
            audit_type=audit_type,
            status=status,
            user_id=str(user.id),
            user_name=user.name,
            user_role=user.role,
            user_email=user.email,
            action=action,
            request_meta={
                'memo_id': memo.id,
                'reference_number': memo.reference_number,
                'status': memo.status,
            },
            new_values={'status': memo.status}
        )

        # Async task for audit logging
        log_audit_event_task.delay(log_params.__dict__)
