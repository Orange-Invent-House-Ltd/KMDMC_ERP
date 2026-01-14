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
        return CorrespondenceListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Correspondence.objects.none()
    
        user = self.request.user
        if user.role == "general_staff":
            return Correspondence.objects.filter(receiver=user)
        queryset = super().get_queryset()
        return queryset
