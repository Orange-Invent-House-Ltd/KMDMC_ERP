from django.contrib import admin
from hr_config.models import (
    AppraisalTemplate,
    LeaveType,
    PublicHoliday,
    AttendancePolicy,
    LeaveApprovalWorkflow,
    LeaveApprovalStage,
)


class LeaveApprovalStageInline(admin.TabularInline):
    """Inline admin for approval stages within workflow."""
    model = LeaveApprovalStage
    extra = 1
    fields = ['stage_order', 'stage_name', 'approver_type', 'required_role', 'is_required', 'can_skip']
    ordering = ['stage_order']


@admin.register(AppraisalTemplate)
class AppraisalTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for AppraisalTemplate."""
    list_display = ['template_id', 'template_name', 'status', 'created_by', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['template_id', 'template_name', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['template_id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('template_id', 'template_name', 'description', 'status')
        }),
        ('Template Content', {
            'fields': ('template_content',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    """Admin configuration for LeaveType."""
    list_display = ['leave_type_name', 'allowance_days', 'accrual_frequency', 'accrual_rate', 'is_paid', 'is_active']
    list_filter = ['accrual_frequency', 'is_paid', 'is_active', 'requires_documentation']
    search_fields = ['leave_type_name', 'description']
    ordering = ['leave_type_name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('leave_type_name', 'description', 'color_code')
        }),
        ('Allowance & Accrual', {
            'fields': ('allowance_days', 'accrual_frequency', 'accrual_rate')
        }),
        ('Settings', {
            'fields': ('is_paid', 'requires_documentation', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    """Admin configuration for PublicHoliday."""
    list_display = ['holiday_name', 'date', 'year', 'holiday_type', 'is_recurring']
    list_filter = ['year', 'holiday_type', 'is_recurring']
    search_fields = ['holiday_name']
    ordering = ['-date']
    date_hierarchy = 'date'
    readonly_fields = ['year', 'created_at', 'updated_at']

    fieldsets = (
        ('Holiday Information', {
            'fields': ('holiday_name', 'date', 'year', 'holiday_type', 'is_recurring')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(admin.ModelAdmin):
    """Admin configuration for AttendancePolicy (singleton)."""
    list_display = ['shift_start_time', 'shift_end_time', 'late_grace_period_minutes', 'enable_overtime', 'updated_by', 'updated_at']
    readonly_fields = ['updated_at']

    fieldsets = (
        ('Shift Times', {
            'fields': ('shift_start_time', 'shift_end_time')
        }),
        ('Grace Period & Overtime', {
            'fields': ('late_grace_period_minutes', 'enable_overtime', 'overtime_threshold_minutes')
        }),
        ('Working Days', {
            'fields': ('working_days_per_week', 'working_days')
        }),
        ('Check-in/Check-out', {
            'fields': ('require_check_in', 'require_check_out')
        }),
        ('Metadata', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Disable add - only one instance allowed."""
        return not AttendancePolicy.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Disable delete - policy is required."""
        return False


@admin.register(LeaveApprovalWorkflow)
class LeaveApprovalWorkflowAdmin(admin.ModelAdmin):
    """Admin configuration for LeaveApprovalWorkflow."""
    list_display = ['workflow_name', 'is_active', 'enable_auto_approval', 'auto_approve_threshold_days', 'created_at']
    list_filter = ['is_active', 'enable_auto_approval', 'created_at']
    search_fields = ['workflow_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [LeaveApprovalStageInline]

    fieldsets = (
        ('Workflow Information', {
            'fields': ('workflow_name', 'is_active')
        }),
        ('Auto-Approval Settings', {
            'fields': ('enable_auto_approval', 'auto_approve_threshold_days')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaveApprovalStage)
class LeaveApprovalStageAdmin(admin.ModelAdmin):
    """Admin configuration for LeaveApprovalStage."""
    list_display = ['workflow', 'stage_order', 'stage_name', 'approver_type', 'required_role', 'is_required', 'can_skip']
    list_filter = ['approver_type', 'is_required', 'can_skip']
    search_fields = ['stage_name', 'workflow__workflow_name']
    ordering = ['workflow', 'stage_order']

    fieldsets = (
        ('Stage Information', {
            'fields': ('workflow', 'stage_order', 'stage_name')
        }),
        ('Approver Configuration', {
            'fields': ('approver_type', 'required_role')
        }),
        ('Stage Settings', {
            'fields': ('is_required', 'can_skip')
        }),
    )
