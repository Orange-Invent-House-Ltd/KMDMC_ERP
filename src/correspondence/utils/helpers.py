"""
Utility functions for correspondence management.
"""
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import random


def generate_reference_number(correspondence_type='incoming', prefix='KMDMC'):
    """
    Generate a unique reference number for correspondence.
    
    Format: PREFIX/TYPE/YEAR/SEQUENCE
    Example: KMDMC/IN/2026/1234
    
    Args:
        correspondence_type: 'incoming' or 'outgoing'
        prefix: Organization prefix
    
    Returns:
        str: Unique reference number
    """
    year = timezone.now().year
    type_code = 'IN' if correspondence_type == 'incoming' else 'OUT'
    
    # Generate random sequence (in production, use a proper sequence)
    sequence = str(random.randint(1000, 9999))
    
    return f"{prefix}/{type_code}/{year}/{sequence}"


def get_correspondence_stats(queryset=None):
    """
    Calculate comprehensive statistics for correspondence.
    
    Args:
        queryset: Optional filtered queryset. If None, uses all correspondence.
    
    Returns:
        dict: Statistics dictionary
    """
    from correspondence.models import Correspondence
    
    if queryset is None:
        queryset = Correspondence.objects.all()
    
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    stats = {
        'total': queryset.count(),
        'incoming': queryset.filter(correspondence_type='incoming').count(),
        'outgoing': queryset.filter(correspondence_type='outgoing').count(),
        'new': queryset.filter(status='new').count(),
        'pending_action': queryset.filter(status='pending_action').count(),
        'in_progress': queryset.filter(status='in_progress').count(),
        'assigned': queryset.filter(status='assigned').count(),
        'replied': queryset.filter(status='replied').count(),
        'archived': queryset.filter(status='archived').count(),
        'closed': queryset.filter(status='closed').count(),
        'overdue': queryset.filter(
            due_date__lt=today
        ).exclude(status__in=['closed', 'archived']).count(),
        'urgent': queryset.filter(priority='urgent').exclude(
            status__in=['closed', 'archived']
        ).count(),
        'high_priority': queryset.filter(priority='high').exclude(
            status__in=['closed', 'archived']
        ).count(),
        'confidential': queryset.filter(is_confidential=True).count(),
        'requires_action': queryset.filter(requires_action=True).count(),
        'last_7_days': queryset.filter(created_at__date__gte=last_7_days).count(),
        'last_30_days': queryset.filter(created_at__date__gte=last_30_days).count(),
    }
    
    return stats


def create_activity_log(correspondence, action, description, user, metadata=None, is_automated=False):
    """
    Create an activity log entry for correspondence.
    
    Args:
        correspondence: Correspondence instance
        action: Action type (e.g., 'created', 'assigned', 'status_changed')
        description: Human-readable description
        user: User who performed the action
        metadata: Optional dict with additional data
        is_automated: Whether action was automated
    
    Returns:
        CorrespondenceActivity instance
    """
    from correspondence.models import CorrespondenceActivity
    
    return CorrespondenceActivity.objects.create(
        correspondence=correspondence,
        action=action,
        description=description,
        performed_by=user,
        metadata=metadata or {},
        is_automated=is_automated
    )


def get_overdue_correspondence(user=None):
    """
    Get overdue correspondence items.
    
    Args:
        user: Optional user to filter by assignment
    
    Returns:
        QuerySet of overdue correspondence
    """
    from correspondence.models import Correspondence
    
    today = timezone.now().date()
    queryset = Correspondence.objects.filter(
        due_date__lt=today
    ).exclude(status__in=['closed', 'archived'])
    
    if user:
        queryset = queryset.filter(assigned_to=user)
    
    return queryset.order_by('due_date')


def get_pending_for_user(user):
    """
    Get correspondence pending action by a specific user.
    
    Args:
        user: User instance
    
    Returns:
        QuerySet of pending correspondence
    """
    from correspondence.models import Correspondence
    
    return Correspondence.objects.filter(
        assigned_to=user
    ).exclude(
        status__in=['closed', 'archived', 'replied']
    ).order_by('-priority', 'due_date')


def categorize_by_urgency(queryset):
    """
    Categorize correspondence by urgency level.
    
    Args:
        queryset: Correspondence queryset
    
    Returns:
        dict with 'critical', 'high', 'normal', 'low' lists
    """
    today = timezone.now().date()
    
    result = {
        'critical': [],  # Overdue + urgent
        'high': [],      # Urgent or overdue
        'normal': [],    # Normal priority, not overdue
        'low': []        # Low priority
    }
    
    for item in queryset:
        is_overdue = item.due_date and item.due_date < today
        
        if item.priority == 'urgent' and is_overdue:
            result['critical'].append(item)
        elif item.priority == 'urgent' or is_overdue or item.priority == 'high':
            result['high'].append(item)
        elif item.priority == 'low':
            result['low'].append(item)
        else:
            result['normal'].append(item)
    
    return result


def format_reference_search(query):
    """
    Format and normalize reference number search query.
    
    Args:
        query: Search string
    
    Returns:
        str: Normalized search query
    """
    # Remove common prefixes if partial
    query = query.strip().upper()
    
    # Handle partial matches
    if query.startswith('KMDMC'):
        return query
    elif query.startswith('IN/') or query.startswith('OUT/'):
        return f"KMDMC/{query}"
    
    return query
