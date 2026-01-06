from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from dashboard.models import Approval
from dashboard.serializers import ApprovalSerializer


class ApprovalViewSet(viewsets.ModelViewSet):
    queryset = Approval.objects.select_related('requester', 'department').all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'urgency', 'department']
    search_fields = ['subject', 'description', 'requester__name']
    ordering_fields = ['created_at', 'date', 'urgency']

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        urgency = self.request.query_params.get('urgency')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if urgency:
            queryset = queryset.filter(urgency=urgency)
        
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a pending approval request."""
        approval = self.get_object()
        if approval.status != 'pending':
            return Response(
                {'error': 'Only pending approvals can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        approval.status = 'approved'
        approval.save()
        serializer = self.get_serializer(approval)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending approval request."""
        approval = self.get_object()
        if approval.status != 'pending':
            return Response(
                {'error': 'Only pending approvals can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        approval.status = 'rejected'
        approval.save()
        serializer = self.get_serializer(approval)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending approvals."""
        pending_approvals = self.get_queryset().filter(status='pending')
        page = self.paginate_queryset(pending_approvals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(pending_approvals, many=True)
        return Response(serializer.data)
