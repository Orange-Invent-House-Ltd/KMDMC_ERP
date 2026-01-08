from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser, Department, StaffActivity, PerformanceRecord, StaffTask


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head', 'parent', 'is_active', 'staff_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    raw_id_fields = ['head', 'parent']

    def staff_count(self, obj):
        return obj.staff_members.filter(is_active=True).count()
    staff_count.short_description = 'Staff Count'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'name', 'employee_id', 'position', 'department', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'department', 'location', 'is_verified', 'is_active', 'is_staff']
    search_fields = ['email', 'name', 'phone', 'employee_id', 'position']
    ordering = ['-created_at']
    raw_id_fields = ['department', 'reports_to']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'date_of_birth', 'profile_photo', 'bio')}),
        ('Staff Profile', {'fields': ('employee_id', 'position', 'department', 'location', 'date_joined_org', 'reports_to')}),
        ('Contact', {'fields': ('office_phone', 'office_extension')}),
        ('Performance', {'fields': ('performance_score', 'performance_points')}),
        ('Role & Permissions', {'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Notifications', {'fields': ('send_email_notifications', 'send_app_notifications', 'send_sms_notifications')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'employee_id', 'position', 'department', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(StaffActivity)
class StaffActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'activity_count', 'tasks_completed', 'approvals_given', 'activity_level']
    list_filter = ['date', 'user__department']
    search_fields = ['user__name', 'user__email']
    date_hierarchy = 'date'
    raw_id_fields = ['user']

    def activity_level(self, obj):
        level = obj.activity_level
        colors = ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors[level], level
        )
    activity_level.short_description = 'Level'


@admin.register(PerformanceRecord)
class PerformanceRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'performance_score', 'points_earned', 'completion_rate', 'department_rank']
    list_filter = ['month', 'user__department']
    search_fields = ['user__name', 'user__email']
    date_hierarchy = 'month'
    raw_id_fields = ['user']

    def completion_rate(self, obj):
        rate = obj.completion_rate
        color = 'green' if rate >= 80 else 'orange' if rate >= 60 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    completion_rate.short_description = 'Completion Rate'


@admin.register(StaffTask)
class StaffTaskAdmin(admin.ModelAdmin):
    list_display = ['title_short', 'assigned_to', 'assigned_by', 'status_badge', 'priority_badge', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'department', 'due_date']
    search_fields = ['title', 'description', 'assigned_to__name', 'assigned_by__name']
    ordering = ['-created_at']
    raw_id_fields = ['assigned_to', 'assigned_by', 'department']
    date_hierarchy = 'created_at'

    def title_short(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'in_progress': '#17a2b8',
            'completed': '#28a745',
            'overdue': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def priority_badge(self, obj):
        colors = {
            'low': '#6c757d',
            'normal': '#17a2b8',
            'high': '#ffc107',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
