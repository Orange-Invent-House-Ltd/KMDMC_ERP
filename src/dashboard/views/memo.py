from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from dashboard.models import Memo
from dashboard.serializers import MemoSerializer


class MemoViewSet(viewsets.ModelViewSet):
    queryset = Memo.objects.select_related('author', 'department').prefetch_related('recipients').all()
    serializer_class = MemoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'department']
    search_fields = ['title', 'content', 'author__name']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter memos authored by or sent to the current user
        return queryset.filter(
            Q(author=self.request.user) | Q(recipients=self.request.user)
        ).distinct()

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get memos sent by the current user."""
        sent_memos = Memo.objects.filter(author=request.user)
        page = self.paginate_queryset(sent_memos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(sent_memos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received(self, request):
        """Get memos received by the current user."""
        received_memos = Memo.objects.filter(recipients=request.user)
        page = self.paginate_queryset(received_memos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(received_memos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a draft memo."""
        memo = self.get_object()
        memo.status = 'sent'
        memo.save()
        serializer = self.get_serializer(memo)
        return Response(serializer.data)
