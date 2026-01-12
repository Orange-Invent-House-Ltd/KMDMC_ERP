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
    CorrespondenceUpdateSerializer,
    CorrespondenceAssignSerializer,
    CorrespondenceStatusSerializer,

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
        queryset = super().get_queryset()
        
        # Filter by type (incoming/outgoing)
        corr_type = self.request.query_params.get('type')
        if corr_type in ['incoming', 'outgoing']:
            queryset = queryset.filter(correspondence_type=corr_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        date_range = self.request.query_params.get('date_range')
        
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                queryset = queryset.filter(created_at__date=today)
            elif date_range == 'last_7_days':
                queryset = queryset.filter(created_at__date__gte=today - timedelta(days=7))
            elif date_range == 'last_30_days':
                queryset = queryset.filter(created_at__date__gte=today - timedelta(days=30))
            elif date_range == 'last_90_days':
                queryset = queryset.filter(created_at__date__gte=today - timedelta(days=90))
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Filter overdue
        show_overdue = self.request.query_params.get('overdue')
        if show_overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now().date()
            ).exclude(status__in=['closed', 'archived'])
        
        # Filter by assignment
        assigned_to_me = self.request.query_params.get('assigned_to_me')
        if assigned_to_me == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        logged_by_me = self.request.query_params.get('logged_by_me')
        if logged_by_me == 'true':
            queryset = queryset.filter(logged_by=self.request.user)
        
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Retrieve correspondence and log the view activity."""
        instance = self.get_object()
        
        # TODO: Log view activity (only once per session or time period)
        
        serializer = self.get_serializer(instance)
        return Response(
            success = True,
            message = "Correspondence retrieved successfully",
            data = serializer.data,
            status_code = status.HTTP_200_OK,
        )
    

    # =========================================================================
    # Status Management
    # =========================================================================

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change the status of a correspondence item."""
        correspondence = self.get_object()
        serializer = CorrespondenceStatusSerializer(data=request.data)
        
        if serializer.is_valid():
            old_status = correspondence.status
            new_status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')
            
            correspondence.status = new_status
            correspondence.save()
            
        #     event = LogParams(
        #     audit_type=AuditTypeEnum.CHANGE_CORRESPONDENCE_STATUS.raw_value,
        #     audit_module=AuditModuleEnum.AUDIT.raw_value,
        #     status=AuditStatusEnum.SUCCESS.raw_value,
        #     user_id=str(request.user.id),
        #     user_name=request.user.name.upper(),
        #     user_email=request.user.email,
        #     user_role=request.user.role.name,
        #     action=f"{request.user.name.upper()} changed correspondence status from {old_status} to {new_status}",
        #     request_meta=extract_api_request_metadata(request),
        # )
        # log_audit_event_task.delay(event.__dict__)
        
        return Response(
            success=True,
            message = "Correspondence status updated successfully",
            data=serializer.data,
            status_code=status.HTTP_400_BAD_REQUEST
        )

 
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign correspondence to a user."""
        correspondence = self.get_object()
        serializer = CorrespondenceAssignSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = serializer.validated_data['assigned_to_id']
            notes = serializer.validated_data.get('notes', '')
            
            assigned_user = get_object_or_404(User, id=user_id)
            old_assigned = correspondence.assigned_to
            
            correspondence.assigned_to = assigned_user
            correspondence.assigned_by = request.user
            correspondence.assigned_at = timezone.now()
            
            # Update status if new
            if correspondence.status == 'new':
                correspondence.status = 'assigned'
            
            correspondence.save()
            
            # Log activity
            description = f"Assigned to {assigned_user.name}"
            if old_assigned:
                description = f"Reassigned from {old_assigned.name} to {assigned_user.name}"
            if notes:
                description += f". Notes: {notes}"
            
            CorrespondenceActivity.objects.create(
                correspondence=correspondence,
                action='assigned',
                description=description,
                performed_by=request.user,
                metadata={
                    'assigned_to_id': user_id,
                    'assigned_to_name': assigned_user.name,
                    'notes': notes
                }
            )
            
            return Response(CorrespondenceSerializer(correspondence).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get correspondence assigned to the current user."""
        queryset = self.get_queryset().filter(assigned_to=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CorrespondenceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CorrespondenceListSerializer(queryset, many=True)
        return Response(serializer.data)

   
    
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

