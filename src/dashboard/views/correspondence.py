from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from dashboard.models import Correspondence
from dashboard.serializers import CorrespondenceSerializer


class CorrespondenceViewSet(viewsets.ModelViewSet):
    queryset = Correspondence.objects.all()
    serializer_class = CorrespondenceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['correspondence_type', 'status', 'action_required']
    search_fields = ['title', 'description', 'sender']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()
        corr_type = self.request.query_params.get('type')
        status_filter = self.request.query_params.get('status')
        
        if corr_type:
            queryset = queryset.filter(correspondence_type=corr_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    @action(detail=False, methods=['get'])
    def incoming(self, request):
        """Get all incoming correspondence."""
        incoming = self.get_queryset().filter(correspondence_type='incoming')
        page = self.paginate_queryset(incoming)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(incoming, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def outgoing(self, request):
        """Get all outgoing correspondence."""
        outgoing = self.get_queryset().filter(correspondence_type='outgoing')
        page = self.paginate_queryset(outgoing)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(outgoing, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def action_required(self, request):
        """Get all correspondence requiring action."""
        action_items = self.get_queryset().filter(action_required=True)
        page = self.paginate_queryset(action_items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(action_items, many=True)
        return Response(serializer.data)
