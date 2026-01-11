from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser, Department, StaffActivity, PerformanceRecord


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head', 'is_active', 'staff_count']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    raw_id_fields = ['head']

    def staff_count(self, obj):
        return obj.staff_members.filter(is_active=True).count()
    staff_count.short_description = 'Staff Count'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'name', 'employee_id', 'position', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'location', 'is_verified', 'is_active', 'is_staff']
    search_fields = ['email', 'name', 'phone', 'employee_id', 'position']
    ordering = ['-created_at']
    
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


