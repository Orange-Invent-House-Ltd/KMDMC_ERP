from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class Memo(models.Model):
    """Main Memo model with KMGMC-MEMO-YYYY-### reference format."""

    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    # Core Fields
    reference_number = models.CharField(max_length=100, unique=True, db_index=True)

    # Participants
    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_memos',
        help_text="Person who created the memo"
    )

    to_unit_head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='memos_to_review',
        help_text="Unit Head who will review the memo"
    )

    through_cc = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memos_ccd',
        help_text="General Manager (for notification only, not approval)"
    )

    final_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memos_to_approve',
        help_text="Director/MD for final approval"
    )

    # Content Fields
    subject = models.CharField(max_length=500)
    content = models.TextField(help_text="Rich text content of the memo")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    # Status Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    current_stage = models.IntegerField(
        default=1,
        help_text="1=Draft, 2=Review, 3=Approval"
    )

    # Reference Number Generation Fields
    yearly_serial = models.PositiveIntegerField(null=True, blank=True)
    serial_year = models.IntegerField(null=True, blank=True)

    # Locking mechanism
    is_locked = models.BooleanField(
        default=False,
        help_text="True when submitted for approval, prevents editing"
    )
    locked_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Memo'
        verbose_name_plural = 'Memos'
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['initiator', 'status']),
        ]

    def __str__(self):
        return f"{self.reference_number} - {self.subject[:50]}"

    def save(self, *args, **kwargs):
        """Generate reference number on creation: KMGMC-MEMO-YYYY-###"""
        if not self.reference_number:
            current_year = timezone.now().year

            # Get last serial number for current year
            last_memo = (
                Memo.objects
                .filter(serial_year=current_year)
                .aggregate(models.Max("yearly_serial"))
                .get("yearly_serial__max") or 0
            )

            self.yearly_serial = last_memo + 1
            self.serial_year = current_year

            # Format: KMGMC-MEMO-2024-001
            self.reference_number = f"KMGMC-MEMO-{current_year}-{self.yearly_serial:03d}"

        super().save(*args, **kwargs)

    @property
    def can_edit(self):
        """Can only edit if in draft status and not locked."""
        return self.status == 'draft' and not self.is_locked

    @property
    def can_cancel(self):
        """Can only cancel if in draft status."""
        return self.status == 'draft'


class MemoApproval(models.Model):
    """Tracks approval history for each stage of memo workflow."""

    STAGE_CHOICES = [
        (1, 'Draft'),
        (2, 'Review (Unit Head)'),
        (3, 'Approval (Director/MD)'),
    ]

    ACTION_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned for Revision'),
    ]

    memo = models.ForeignKey(
        Memo,
        on_delete=models.CASCADE,
        related_name='approvals'
    )

    stage = models.IntegerField(choices=STAGE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='memo_actions',
        help_text="User who performed the action"
    )

    comments = models.TextField(blank=True, help_text="Approval/rejection comments")

    # Timestamp
    action_date = models.DateTimeField(auto_now_add=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-action_date']
        verbose_name = 'Memo Approval'
        verbose_name_plural = 'Memo Approvals'
        indexes = [
            models.Index(fields=['memo', 'stage']),
            models.Index(fields=['actor', 'action_date']),
        ]

    def __str__(self):
        return f"{self.memo.reference_number} - Stage {self.stage} - {self.action}"


class MemoAttachment(models.Model):
    """File attachments for memos with metadata."""

    memo = models.ForeignKey(
        Memo,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    file = models.FileField(
        upload_to='memo_attachments/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx',
                                   'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'txt']
            )
        ]
    )

    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=100, help_text="MIME type")

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_memo_attachments'
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Optional metadata
    description = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Memo Attachment'
        verbose_name_plural = 'Memo Attachments'

    def __str__(self):
        return f"{self.memo.reference_number} - {self.file_name}"

    @property
    def file_size_display(self):
        """Human-readable file size."""
        size_bytes = self.file_size
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
