from rest_framework import viewsets, status
from rest_framework.decorators import action
from utils.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from datetime import timedelta
from audit.enums import AuditModuleEnum, AuditStatusEnum, AuditTypeEnum, LogParams
from audit.tasks import log_audit_event_task
from correspondence.models import Correspondence
from correspondence.serializers import (
    CorrespondenceSerializer,
    CorrespondenceListSerializer,
    CorrespondenceCreateSerializer,
    CorrespondenceUpdateSerializer
)

User = get_user_model()


class CorrespondenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing correspondence (incoming and outgoing mail).
    """
    queryset = Correspondence.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        'correspondence_type', 'status', 'priority',
        'category', 'assigned_to',
        'is_confidential', 'requires_action'
    ]
    search_fields = [
        'reference_number', 'external_reference', 'subject',
        'summary', 'contact_name'
    ]
    ordering_fields = [
        'created_at', 'date_sent',
        'due_date', 'priority', 'status'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CorrespondenceListSerializer
        elif self.action == 'create':
            return CorrespondenceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CorrespondenceUpdateSerializer
        return CorrespondenceSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Correspondence.objects.none()
    
        user = self.request.user
        if user.role == "general_staff":
            return Correspondence.objects.filter(receiver=user)
        queryset = super().get_queryset()
        return queryset
   
    
    # @action(detail=False, methods=['get'])
    # def statistics(self, request):
    #     """Get comprehensive correspondence statistics."""
    #     today = timezone.now().date()
    #     queryset = self.get_queryset()
        
    #     # Base counts
    #     total = queryset.count()
    #     incoming = queryset.filter(correspondence_type='incoming').count()
    #     outgoing = queryset.filter(correspondence_type='outgoing').count()
        
    #     # Status counts
    #     by_status = {}
    #     for status_code, status_name in Correspondence.STATUS_CHOICES:
    #         count = queryset.filter(status=status_code).count()
    #         by_status[status_code] = {
    #             'label': status_name,
    #             'count': count
    #         }
        
    #     # Priority counts
    #     by_priority = {}
    #     for priority_code, priority_name in Correspondence.PRIORITY_CHOICES:
    #         count = queryset.filter(priority=priority_code).count()
    #         by_priority[priority_code] = {
    #             'label': priority_name,
    #             'count': count
    #         }
        
    #     # Category breakdown
    #     by_category = list(
    #         queryset.exclude(category__isnull=True)
    #         .values('category__id', 'category__name', 'category__color')
    #         .annotate(count=Count('id'))
    #         .order_by('-count')
    #     )
        
    #     # Overdue count
    #     overdue = queryset.filter(
    #         due_date__lt=today
    #     ).exclude(status__in=['closed', 'archived']).count()
        
    #     # Recent trend (last 7 days)
    #     recent_trend = []
    #     for i in range(7):
    #         date = today - timedelta(days=i)
    #         count = queryset.filter(created_at__date=date).count()
    #         recent_trend.append({
    #             'date': date.isoformat(),
    #             'count': count
    #         })
    #     recent_trend.reverse()
        
    #     stats = {
    #         'total': total,
    #         'incoming': incoming,
    #         'outgoing': outgoing,
    #         'pending_action': by_status.get('pending_action', {}).get('count', 0),
    #         'in_progress': by_status.get('in_progress', {}).get('count', 0),
    #         'overdue': overdue,
    #         'by_status': by_status,
    #         'by_category': by_category,
    #         'by_priority': by_priority,
    #         'recent_trend': recent_trend,
    #     }
        
    #     return Response(stats)

    # @action(detail=False, methods=['get'])
    # def dashboard_summary(self, request):
    #     """Get summary data for dashboard widgets."""
    #     today = timezone.now().date()
    #     last_7_days = today - timedelta(days=7)
    #     queryset = self.get_queryset()
        
    #     summary = {
    #         'total_incoming': queryset.filter(correspondence_type='incoming').count(),
    #         'total_outgoing': queryset.filter(correspondence_type='outgoing').count(),
    #         'new_this_week': queryset.filter(created_at__date__gte=last_7_days).count(),
    #         'pending_action': queryset.filter(status='pending_action').count(),
    #         'urgent': queryset.filter(priority='urgent').exclude(
    #             status__in=['closed', 'archived']
    #         ).count(),
    #         'overdue': queryset.filter(
    #             due_date__lt=today
    #         ).exclude(status__in=['closed', 'archived']).count(),
    #         'my_assignments': queryset.filter(assigned_to=request.user).count(),
    #         'recent': CorrespondenceListSerializer(
    #             queryset[:5], many=True
    #         ).data,
    #     }
        
    #     return Response(summary)

