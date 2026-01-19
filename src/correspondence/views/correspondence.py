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
from console.permissions import permissions_required
from utils.permissions import PERMISSIONS

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
        if self.action == ['list', 'retrieve']:
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
    
    @permissions_required([PERMISSIONS.CAN_VIEW_CORRESPONDENCE])
    def list(self, request, *args, **kwargs):
        """Override list to return custom response format."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            message="Correspondence retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @permissions_required([PERMISSIONS.CAN_VIEW_CORRESPONDENCE])
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return custom response format."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Correspondence retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    
    @permissions_required([PERMISSIONS.CAN_CREATE_CORRESPONDENCE])
    def create(self, request, *args, **kwargs):
        """Override create to return custom response format."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(sender=request.user)
        return Response(
            success=True,
            message="Correspondence created successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )
    
    @permissions_required([PERMISSIONS.CAN_UPDATE_CORRESPONDENCE])
    def update(self, request, *args, **kwargs):
        """Override update to return custom response format."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            success=True,
            message="Correspondence updated successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )