from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


class AppraisalTemplate(models.Model):
    """
    Template for employee appraisals with structured JSON content.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]

    template_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated e.g., APP-2024-001"
    )
    template_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    template_content = models.JSONField(
        default=dict,
        help_text="Structured template with sections, questions, and KPIs"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appraisal_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Appraisal Template'
        verbose_name_plural = 'Appraisal Templates'

    def __str__(self):
        return f"{self.template_id} - {self.template_name}"

    def save(self, *args, **kwargs):
        if not self.template_id:
            # Generate template_id: APP-{YEAR}-{SERIAL}
            year = timezone.now().year
            last_template = AppraisalTemplate.objects.filter(
                template_id__startswith=f'APP-{year}-'
            ).order_by('-template_id').first()

            if last_template:
                # Extract serial number and increment
                last_serial = int(last_template.template_id.split('-')[-1])
                new_serial = last_serial + 1
            else:
                new_serial = 1

            self.template_id = f'APP-{year}-{new_serial:03d}'

        super().save(*args, **kwargs)

    def clean(self):
        """Validate template_content JSON structure."""
        if self.template_content:
            if not isinstance(self.template_content, dict):
                raise ValidationError("template_content must be a JSON object")
            if 'sections' not in self.template_content:
                raise ValidationError("template_content must contain 'sections' key")


class LeaveType(models.Model):
    """
    Configuration for different types of leave (Annual, Sick, Maternity, etc.)
    """
    ACCRUAL_FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('per_event', 'Per Event'),
    ]

    leave_type_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    allowance_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Total days allowed (e.g., 30 for annual, 90 for maternity)"
    )
    accrual_frequency = models.CharField(
        max_length=20,
        choices=ACCRUAL_FREQUENCY_CHOICES,
        default='yearly',
        help_text="How the allowance accrues"
    )
    accrual_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Days accrued per period (e.g., 2.5 days/month for annual leave)"
    )
    requires_documentation = models.BooleanField(
        default=False,
        help_text="Whether this leave type requires supporting documents"
    )
    is_paid = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    color_code = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hex color for calendar display"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['leave_type_name']
        verbose_name = 'Leave Type'
        verbose_name_plural = 'Leave Types'

    def __str__(self):
        return f"{self.leave_type_name} ({self.allowance_days} days)"

    def calculate_accrual_rate(self):
        """Auto-calculate accrual rate based on frequency."""
        if self.accrual_frequency == 'monthly':
            return self.allowance_days / 12
        elif self.accrual_frequency == 'yearly':
            return self.allowance_days
        else:  # per_event
            return self.allowance_days


class PublicHoliday(models.Model):
    """
    Public holidays that affect leave calculations and attendance.
    """
    HOLIDAY_TYPE_CHOICES = [
        ('official', 'Official Holiday'),
        ('observance', 'Observance'),
        ('restricted', 'Restricted Holiday'),
    ]

    holiday_name = models.CharField(max_length=255)
    date = models.DateField()
    year = models.IntegerField(editable=False)
    holiday_type = models.CharField(
        max_length=20,
        choices=HOLIDAY_TYPE_CHOICES,
        default='official'
    )
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(
        default=False,
        help_text="Whether this holiday repeats annually on the same date"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        unique_together = ['holiday_name', 'date']
        verbose_name = 'Public Holiday'
        verbose_name_plural = 'Public Holidays'

    def __str__(self):
        return f"{self.holiday_name} ({self.date.strftime('%B %d, %Y')})"

    def save(self, *args, **kwargs):
        # Auto-set year from date
        if self.date:
            self.year = self.date.year
        super().save(*args, **kwargs)


class AttendancePolicy(models.Model):
    """
    Organization-wide attendance policy settings (Singleton).
    Only one instance should exist.
    """
    shift_start_time = models.TimeField(
        default='09:00',
        help_text="Default shift start time (e.g., 09:00)"
    )
    shift_end_time = models.TimeField(
        default='17:00',
        help_text="Default shift end time (e.g., 17:00)"
    )
    late_grace_period_minutes = models.IntegerField(
        default=15,
        help_text="Minutes allowed after shift start before marked late"
    )
    enable_overtime = models.BooleanField(
        default=True,
        help_text="Whether overtime tracking is enabled"
    )
    overtime_threshold_minutes = models.IntegerField(
        default=30,
        help_text="Minutes after shift end to qualify as overtime"
    )
    working_days_per_week = models.IntegerField(
        default=5,
        help_text="Number of working days per week"
    )
    working_days = models.JSONField(
        default=list,
        help_text="Array of working days: ['monday', 'tuesday', etc.]"
    )
    require_check_in = models.BooleanField(default=True)
    require_check_out = models.BooleanField(default=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendance_policy_updates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Attendance Policy'
        verbose_name_plural = 'Attendance Policy'

    def __str__(self):
        return f"Attendance Policy (Updated: {self.updated_at.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (Singleton pattern)
        if not self.pk and AttendancePolicy.objects.exists():
            raise ValidationError(
                "Only one AttendancePolicy instance is allowed. "
                "Please update the existing policy instead."
            )

        # Set default working days if not provided
        if not self.working_days:
            self.working_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

        super().save(*args, **kwargs)

    @classmethod
    def get_policy(cls):
        """Get or create the singleton instance."""
        policy, created = cls.objects.get_or_create(pk=1)
        return policy


class LeaveApprovalWorkflow(models.Model):
    """
    Configurable multi-stage approval workflow for leave requests.
    """
    workflow_name = models.CharField(
        max_length=255,
        default='Default Leave Approval'
    )
    is_active = models.BooleanField(default=True)
    auto_approve_threshold_days = models.IntegerField(
        default=2,
        help_text="Auto-approve leave requests less than this many days"
    )
    enable_auto_approval = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Leave Approval Workflow'
        verbose_name_plural = 'Leave Approval Workflows'

    def __str__(self):
        return self.workflow_name

    @classmethod
    def get_active_workflow(cls):
        """Get the currently active workflow."""
        return cls.objects.filter(is_active=True).first()


class LeaveApprovalStage(models.Model):
    """
    Individual stages in a leave approval workflow.
    """
    APPROVER_TYPE_CHOICES = [
        ('initiator', 'Staff Member (Initiator)'),
        ('direct_manager', 'Direct Manager'),
        ('hr_admin', 'HR Admin'),
        ('department_head', 'Department Head'),
        ('ceo', 'CEO/Executive'),
    ]

    workflow = models.ForeignKey(
        LeaveApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name='stages'
    )
    stage_order = models.IntegerField(
        help_text="Order of this stage in workflow (1, 2, 3, etc.)"
    )
    stage_name = models.CharField(max_length=100)
    approver_type = models.CharField(
        max_length=30,
        choices=APPROVER_TYPE_CHOICES
    )
    required_role = models.ForeignKey(
        'user.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Specific role required to approve at this stage"
    )
    is_required = models.BooleanField(
        default=True,
        help_text="Whether this stage is mandatory"
    )
    can_skip = models.BooleanField(
        default=False,
        help_text="Whether this stage can be skipped under certain conditions"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['workflow', 'stage_order']
        unique_together = ['workflow', 'stage_order']
        verbose_name = 'Leave Approval Stage'
        verbose_name_plural = 'Leave Approval Stages'

    def __str__(self):
        return f"{self.workflow.workflow_name} - Stage {self.stage_order}: {self.stage_name}"
