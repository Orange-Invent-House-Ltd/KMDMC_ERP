from django.contrib import admin
from .models import Approval
from correspondence.models import Correspondence


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['subject', 'requester', 'urgency', 'status', 'date', 'created_at']
    list_filter = ['status', 'urgency', 'date']
    search_fields = ['subject', 'description', 'requester__name', 'requester__email']
    raw_id_fields = ['requester']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']