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
    CorrespondenceStatsSerializer,
)

User = get_user_model()


class CorrespondenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing correspondence (incoming and outgoing mail).
    
    Provides comprehensive CRUD operations, filtering, assignment,
    status management, and statistics for correspondence items.
    """
    queryset = Correspondence.objects.select_related(
        'category', 'classification',
        'assigned_to', 'assigned_by', 'logged_by'
    ).prefetch_related('documents', 'activities', 'comments').all()
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
    # Correspondence Type Filters
    # =========================================================================

    @action(detail=False, methods=['get'])
    def incoming(self, request):
        """Get all incoming correspondence."""
        queryset = self.filter_queryset(
            self.get_queryset().filter(correspondence_type='incoming')
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CorrespondenceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CorrespondenceListSerializer(queryset, many=True)
        event = LogParams(
            audit_type=AuditTypeEnum.VIEW_CORRESPONDENCE.raw_value,
            audit_module=AuditModuleEnum.AUDIT.raw_value,
            status=AuditStatusEnum.SUCCESS.raw_value,
            user_id=str(request.user.id),
            user_name=request.user.name.upper(),
            user_email=request.user.email,
            user_role=request.user.role.name,
            action=f"{request.user.name.upper()} viewed incoming correspondence",
            request_meta=extract_api_request_metadata(request),
        )
        log_audit_event_task.delay(event.__dict__)
        return Response(
            success=True,
            message="Incoming correspondence retrieved successfully",
            data=serializer.data,
            status_code =status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def outgoing(self, request):
        """Get all outgoing correspondence."""
        queryset = self.filter_queryset(
            self.get_queryset().filter(correspondence_type='outgoing')
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CorrespondenceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CorrespondenceListSerializer(queryset, many=True)
        event = LogParams(
            audit_type=AuditTypeEnum.VIEW_CORRESPONDENCE.raw_value,
            audit_module=AuditModuleEnum.AUDIT.raw_value,
            status=AuditStatusEnum.SUCCESS.raw_value,
            user_id=str(request.user.id),
            user_name=request.user.name.upper(),
            user_email=request.user.email,
            user_role=request.user.role.name,
            action=f"{request.user.name.upper()} viewed outgoing correspondence",
            request_meta=extract_api_request_metadata(request),
        )
        log_audit_event_task.delay(event.__dict__)
        
        return Response(
            success=True,
            message="Outgoing correspondence retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
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
            
            event = LogParams(
            audit_type=AuditTypeEnum.CHANGE_CORRESPONDENCE_STATUS.raw_value,
            audit_module=AuditModuleEnum.AUDIT.raw_value,
            status=AuditStatusEnum.SUCCESS.raw_value,
            user_id=str(request.user.id),
            user_name=request.user.name.upper(),
            user_email=request.user.email,
            user_role=request.user.role.name,
            action=f"{request.user.name.upper()} changed correspondence status from {old_status} to {new_status}",
            request_meta=extract_api_request_metadata(request),
        )
        log_audit_event_task.delay(event.__dict__)
        
        return Response(
            success=True,
            message = "Correspondence status updated successfully",
            data=serializer.data,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a correspondence item."""
        correspondence = self.get_object()
        old_status = correspondence.status
        correspondence.status = 'archived'
        correspondence.save()
        
        event = LogParams(
            audit_type=AuditTypeEnum.ARCHIVE_CORRESPONDENCE.raw_value,
            audit_module=AuditModuleEnum.AUDIT.raw_value,
            status=AuditStatusEnum.SUCCESS.raw_value,
            user_id=str(request.user.id),
            user_name=request.user.name.upper(),
            user_email=request.user.email,
            user_role=request.user.role.name,
            action=f"{request.user.name.upper()} archived correspondence",
            request_meta=extract_api_request_metadata(request),
        )
        log_audit_event_task.delay(event.__dict__)
        
        return Response(
            success=True,
            message="Correspondence archived successfully",
            data=CorrespondenceSerializer(correspondence).data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a correspondence item."""
        correspondence = self.get_object()
        old_status = correspondence.status
        correspondence.status = 'closed'
        correspondence.save()
        
        CorrespondenceActivity.objects.create(
            correspondence=correspondence,
            action='status_changed',
            description=f"Closed by {request.user.name}",
            performed_by=request.user,
            metadata={'old_status': old_status, 'new_status': 'closed'}
        )
        
        return Response(CorrespondenceSerializer(correspondence).data)

    # =========================================================================
    # Assignment Management
    # =========================================================================

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

    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """Remove assignment from correspondence."""
        correspondence = self.get_object()
        old_assigned = correspondence.assigned_to
        
        if not old_assigned:
            return Response(
                {'error': 'Correspondence is not assigned to anyone'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        correspondence.assigned_to = None
        correspondence.assigned_by = None
        correspondence.assigned_at = None
        correspondence.save()
        
        CorrespondenceActivity.objects.create(
            correspondence=correspondence,
            action='assigned',
            description=f"Unassigned from {old_assigned.name}",
            performed_by=request.user,
            metadata={'old_assigned_id': old_assigned.id}
        )
        
        return Response(CorrespondenceSerializer(correspondence).data)

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

    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """Get unassigned correspondence."""
        queryset = self.get_queryset().filter(assigned_to__isnull=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CorrespondenceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CorrespondenceListSerializer(queryset, many=True)
        return Response(serializer.data)

    # =========================================================================
    # Priority & Action Filters
    # =========================================================================

    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent correspondence."""
        queryset = self.get_queryset().filter(priority='urgent')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CorrespondenceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CorrespondenceListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_action(self, request):
        """Get correspondence pending MD action."""
        queryset = self.get_queryset().filter(status='pending_action')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CorrespondenceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CorrespondenceListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue correspondence."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            due_date__lt=today
        ).exclude(status__in=['closed', 'archived'])
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CorrespondenceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CorrespondenceListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def requires_action(self, request):
        """Get correspondence that requires action."""
        queryset = self.get_queryset().filter(requires_action=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CorrespondenceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CorrespondenceListSerializer(queryset, many=True)
        return Response(serializer.data)

    # =========================================================================
    # Statistics & Analytics
    # =========================================================================

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get comprehensive correspondence statistics."""
        today = timezone.now().date()
        queryset = self.get_queryset()
        
        # Base counts
        total = queryset.count()
        incoming = queryset.filter(correspondence_type='incoming').count()
        outgoing = queryset.filter(correspondence_type='outgoing').count()
        
        # Status counts
        by_status = {}
        for status_code, status_name in Correspondence.STATUS_CHOICES:
            count = queryset.filter(status=status_code).count()
            by_status[status_code] = {
                'label': status_name,
                'count': count
            }
        
        # Priority counts
        by_priority = {}
        for priority_code, priority_name in Correspondence.PRIORITY_CHOICES:
            count = queryset.filter(priority=priority_code).count()
            by_priority[priority_code] = {
                'label': priority_name,
                'count': count
            }
        
        # Category breakdown
        by_category = list(
            queryset.exclude(category__isnull=True)
            .values('category__id', 'category__name', 'category__color')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Overdue count
        overdue = queryset.filter(
            due_date__lt=today
        ).exclude(status__in=['closed', 'archived']).count()
        
        # Recent trend (last 7 days)
        recent_trend = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = queryset.filter(created_at__date=date).count()
            recent_trend.append({
                'date': date.isoformat(),
                'count': count
            })
        recent_trend.reverse()
        
        stats = {
            'total': total,
            'incoming': incoming,
            'outgoing': outgoing,
            'pending_action': by_status.get('pending_action', {}).get('count', 0),
            'in_progress': by_status.get('in_progress', {}).get('count', 0),
            'overdue': overdue,
            'by_status': by_status,
            'by_category': by_category,
            'by_priority': by_priority,
            'recent_trend': recent_trend,
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get summary data for dashboard widgets."""
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        queryset = self.get_queryset()
        
        summary = {
            'total_incoming': queryset.filter(correspondence_type='incoming').count(),
            'total_outgoing': queryset.filter(correspondence_type='outgoing').count(),
            'new_this_week': queryset.filter(created_at__date__gte=last_7_days).count(),
            'pending_action': queryset.filter(status='pending_action').count(),
            'urgent': queryset.filter(priority='urgent').exclude(
                status__in=['closed', 'archived']
            ).count(),
            'overdue': queryset.filter(
                due_date__lt=today
            ).exclude(status__in=['closed', 'archived']).count(),
            'my_assignments': queryset.filter(assigned_to=request.user).count(),
            'recent': CorrespondenceListSerializer(
                queryset[:5], many=True
            ).data,
        }
        
        return Response(summary)

    # =========================================================================
    # Search & Lookup
    # =========================================================================

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search endpoint."""
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        
        queryset = self.get_queryset().filter(
            Q(reference_number__icontains=query) |
            Q(external_reference__icontains=query) |
            Q(subject__icontains=query) |
            Q(summary__icontains=query) |
            Q(contact_name__icontains=query)
        )[:20]
        
        serializer = CorrespondenceListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_reference(self, request):
        """Lookup correspondence by reference number."""
        reference = request.query_params.get('reference')
        if not reference:
            return Response(
                {'error': 'reference parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        correspondence = get_object_or_404(
            Correspondence, reference_number=reference
        )
        serializer = CorrespondenceSerializer(correspondence)
        return Response(serializer.data)

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        """Assign multiple correspondence items to a user."""
        correspondence_ids = request.data.get('correspondence_ids', [])
        user_id = request.data.get('user_id')
        
        if not correspondence_ids or not user_id:
            return Response(
                {'error': 'correspondence_ids and user_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assigned_user = get_object_or_404(User, id=user_id)
        
        updated = Correspondence.objects.filter(
            id__in=correspondence_ids
        ).update(
            assigned_to=assigned_user,
            assigned_by=request.user,
            assigned_at=timezone.now()
        )
        return Response({
            'message': f'{updated} correspondence item(s) assigned',
            'assigned_to': assigned_user.name
        })

    @action(detail=False, methods=['post'])
    def bulk_status_change(self, request):
        """Change status of multiple correspondence items."""
        correspondence_ids = request.data.get('correspondence_ids', [])
        new_status = request.data.get('status')
        
        if not correspondence_ids or not new_status:
            return Response(
                {'error': 'correspondence_ids and status are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = [s[0] for s in Correspondence.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated = Correspondence.objects.filter(
            id__in=correspondence_ids
        ).update(status=new_status)
        
        return Response({
            'message': f'{updated} correspondence item(s) updated',
            'new_status': new_status
        })

    # =========================================================================
    # Dropdown Options
    # =========================================================================

    @action(detail=False, methods=['get'])
    def options(self, request):
        """Get all dropdown options for correspondence forms."""
        options = {
            'types': [
                {'value': c[0], 'label': c[1]}
                for c in Correspondence.TYPE_CHOICES
            ],
            'statuses': [
                {'value': c[0], 'label': c[1]}
                for c in Correspondence.STATUS_CHOICES
            ],
            'priorities': [
                {'value': c[0], 'label': c[1]}
                for c in Correspondence.PRIORITY_CHOICES
            ],
            'users': list(
                User.objects.filter(is_active=True)
                .values('id', 'name', 'email', 'role')
            ),
        }
        
        return Response(options)
