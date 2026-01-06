from django.contrib import admin
from .models import (
    Department, Approval, Task, Correspondence, 
    Memo, DepartmentPerformance
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['subject', 'requester', 'department', 'urgency', 'status', 'date', 'created_at']
    list_filter = ['status', 'urgency', 'department', 'date']
    search_fields = ['subject', 'description', 'requester__name', 'requester__email']
    raw_id_fields = ['requester', 'department']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'assigned_by', 'department', 'priority', 'status', 'due_date']
    list_filter = ['status', 'priority', 'department']
    search_fields = ['title', 'description', 'assigned_to__name', 'assigned_by__name']
    raw_id_fields = ['assigned_to', 'assigned_by', 'department']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Correspondence)
class CorrespondenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'sender', 'correspondence_type', 'status', 'action_required', 'created_at']
    list_filter = ['correspondence_type', 'status', 'action_required']
    search_fields = ['title', 'description', 'sender']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'department', 'status', 'created_at']
    list_filter = ['status', 'department']
    search_fields = ['title', 'content', 'author__name']
    raw_id_fields = ['author', 'department']
    filter_horizontal = ['recipients']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(DepartmentPerformance)
class DepartmentPerformanceAdmin(admin.ModelAdmin):
    list_display = ['department', 'month', 'performance_score', 'created_at']
    list_filter = ['department', 'month']
    search_fields = ['department__name']
    raw_id_fields = ['department']
    date_hierarchy = 'month'
    ordering = ['-month', '-performance_score']
