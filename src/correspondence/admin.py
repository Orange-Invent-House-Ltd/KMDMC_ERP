from django.contrib import admin
from .models import Correspondence


@admin.register(Correspondence)
class CorrespondenceAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'requires_action', 'created_at']
    search_fields = ['subject', 'receiver__name', 'receiver__email']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
