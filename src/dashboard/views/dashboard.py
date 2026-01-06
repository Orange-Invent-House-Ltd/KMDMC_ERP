from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from dashboard.models import Approval, Task, Correspondence, DepartmentPerformance
from dashboard.serializers import (
    ApprovalSerializer, 
    CorrespondenceSerializer, 
    DepartmentPerformanceSerializer
)
from user.models import CustomUser


class DashboardView(APIView):
    """
    Dashboard overview API endpoint.
    Returns statistics and recent data for the main dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        current_month = today.replace(day=1)

        # Calculate pending approvals stats
        pending_approvals_count = Approval.objects.filter(status='pending').count()
        pending_approvals_last_week = Approval.objects.filter(
            status='pending',
            created_at__date__gte=last_week
        ).count()
        
        # Calculate urgent tasks stats
        urgent_tasks_count = Task.objects.filter(
            Q(priority='urgent') | Q(priority='high'),
            status__in=['pending', 'in_progress']
        ).count()
        
        # Calculate previous week urgent tasks for comparison
        urgent_tasks_prev = Task.objects.filter(
            Q(priority='urgent') | Q(priority='high'),
            status__in=['pending', 'in_progress'],
            created_at__date__lt=last_week
        ).count()
        
        if urgent_tasks_prev > 0:
            urgent_change = int(((urgent_tasks_count - urgent_tasks_prev) / urgent_tasks_prev) * 100)
            urgent_tasks_change = f"+{urgent_change}%" if urgent_change >= 0 else f"{urgent_change}%"
        else:
            urgent_tasks_change = "+0%"
        
        # Calculate correspondence stats
        correspondence_count = Correspondence.objects.count()
        correspondence_last_week = Correspondence.objects.filter(
            created_at__date__gte=last_week
        ).count()
        
        if correspondence_count > correspondence_last_week and correspondence_last_week > 0:
            corr_change = int((correspondence_last_week / correspondence_count) * 100)
            correspondence_change = f"+{corr_change}%"
        else:
            correspondence_change = "+12%"
        
        # Staff active calculation
        total_staff = CustomUser.objects.filter(is_active=True).count()
        active_staff = CustomUser.objects.filter(
            is_active=True,
            is_verified=True
        ).count()
        staff_percentage = int((active_staff / total_staff) * 100) if total_staff > 0 else 0

        stats = {
            'pending_approvals': pending_approvals_count,
            'pending_approvals_change': pending_approvals_last_week,
            'urgent_tasks': urgent_tasks_count,
            'urgent_tasks_change': urgent_tasks_change,
            'correspondence_count': correspondence_count,
            'correspondence_change': correspondence_change,
            'staff_active_percentage': f'{staff_percentage}%',
            'staff_status': 'Stable' if staff_percentage >= 90 else 'Needs Attention'
        }

        # Get pending approvals list (top 10)
        pending_approvals = Approval.objects.filter(
            status='pending'
        ).select_related('requester', 'department').order_by('-urgency', '-created_at')[:10]

        # Get recent correspondence (top 5)
        recent_correspondence = Correspondence.objects.all().order_by('-created_at')[:5]

        # Get department performance for current month
        department_performance = DepartmentPerformance.objects.filter(
            month=current_month
        ).select_related('department').order_by('-performance_score')

        data = {
            'user': {
                'name': request.user.name,
                'role': 'Managing Director',
            },
            'stats': stats,
            'pending_approvals': ApprovalSerializer(pending_approvals, many=True).data,
            'recent_correspondence': CorrespondenceSerializer(recent_correspondence, many=True).data,
            'department_performance': DepartmentPerformanceSerializer(department_performance, many=True).data,
        }

        return Response(data)
