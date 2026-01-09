from django.contrib import admin
from .models import ( Approval, Task,
)
from correspondence.models import Correspondence


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['subject', 'requester', 'urgency', 'status', 'date', 'created_at']
    list_filter = ['status', 'urgency', 'date']
    search_fields = ['subject', 'description', 'requester__name', 'requester__email']
    raw_id_fields = ['requester']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'assigned_by', 'priority', 'status', 'deadline']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'description', 'assigned_to__name', 'assigned_by__name']
    raw_id_fields = ['assigned_to', 'assigned_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
