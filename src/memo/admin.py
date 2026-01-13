from django.contrib import admin
from .models import Memo, MemoApproval, MemoAttachment


class MemoApprovalInline(admin.TabularInline):
    model = MemoApproval
    extra = 0
    readonly_fields = ['stage', 'action', 'actor', 'comments', 'action_date']
    can_delete = False
    fields = ['stage', 'action', 'actor', 'comments', 'action_date']


class MemoAttachmentInline(admin.TabularInline):
    model = MemoAttachment
    extra = 1
    readonly_fields = ['uploaded_by', 'uploaded_at', 'file_size']
    fields = ['file', 'file_name', 'file_size', 'file_type', 'description', 'uploaded_by', 'uploaded_at']


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'subject', 'initiator', 'to_unit_head',
        'status', 'priority', 'current_stage', 'created_at'
    ]
    list_filter = ['status', 'priority', 'current_stage', 'created_at']
    search_fields = ['reference_number', 'subject', 'content']
    readonly_fields = [
        'reference_number', 'yearly_serial', 'serial_year',
        'is_locked', 'locked_at', 'submitted_at', 'reviewed_at',
        'approved_at', 'rejected_at', 'created_at', 'updated_at'
    ]
    inlines = [MemoAttachmentInline, MemoApprovalInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('reference_number', 'subject', 'content', 'priority')
        }),
        ('Workflow', {
            'fields': ('initiator', 'to_unit_head', 'through_cc', 'final_approver')
        }),
        ('Status', {
            'fields': ('status', 'current_stage', 'is_locked')
        }),
        ('Reference Number Generation', {
            'fields': ('yearly_serial', 'serial_year'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'submitted_at', 'reviewed_at', 'approved_at', 'rejected_at',
                'locked_at', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related(
            'initiator', 'to_unit_head', 'through_cc', 'final_approver'
        )


@admin.register(MemoApproval)
class MemoApprovalAdmin(admin.ModelAdmin):
    list_display = ['memo', 'stage', 'action', 'actor', 'action_date']
    list_filter = ['stage', 'action', 'action_date']
    search_fields = ['memo__reference_number', 'comments']
    readonly_fields = ['action_date']

    fieldsets = (
        ('Approval Information', {
            'fields': ('memo', 'stage', 'action', 'actor', 'comments')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'action_date'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('memo', 'actor')


@admin.register(MemoAttachment)
class MemoAttachmentAdmin(admin.ModelAdmin):
    list_display = ['memo', 'file_name', 'file_size_display', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['memo__reference_number', 'file_name']
    readonly_fields = ['uploaded_at', 'file_size']

    fieldsets = (
        ('Attachment Information', {
            'fields': ('memo', 'file', 'file_name', 'file_type', 'file_size', 'description')
        }),
        ('Upload Details', {
            'fields': ('uploaded_by', 'uploaded_at')
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('memo', 'uploaded_by')
