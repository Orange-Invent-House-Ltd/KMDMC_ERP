from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from rest_framework import filters
from django.db import transaction

from utils.response import Response
from utils.pagination import CustomPagination
from console.permissions import IsSuperAdmin
from hr_config.models import LeaveApprovalWorkflow, LeaveApprovalStage
from hr_config.serializers import (
    LeaveApprovalWorkflowListSerializer,
    LeaveApprovalWorkflowDetailSerializer,
    LeaveApprovalWorkflowCreateSerializer,
    LeaveApprovalWorkflowUpdateSerializer,
    LeaveApprovalStageCreateSerializer,
)


class LeaveApprovalWorkflowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave approval workflows.
    Only HR admins/superadmins can manage workflows.
    """
    queryset = LeaveApprovalWorkflow.objects.prefetch_related('stages').all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['is_active']
    search_fields = ['workflow_name']
    ordering_fields = ['created_at', 'updated_at', 'workflow_name']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return LeaveApprovalWorkflowListSerializer
        elif self.action == 'retrieve':
            return LeaveApprovalWorkflowDetailSerializer
        elif self.action == 'create':
            return LeaveApprovalWorkflowCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LeaveApprovalWorkflowUpdateSerializer
        return LeaveApprovalWorkflowListSerializer

    def list(self, request, *args, **kwargs):
        """List all leave approval workflows."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            message="Leave approval workflows retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve single workflow with all stages."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Leave approval workflow retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create new workflow with nested stages."""
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        workflow = serializer.save()

        # Return full details with stages
        workflow_with_stages = LeaveApprovalWorkflow.objects.prefetch_related('stages').get(
            pk=workflow.pk
        )
        response_serializer = LeaveApprovalWorkflowDetailSerializer(workflow_with_stages)

        return Response(
            success=True,
            message="Leave approval workflow created successfully",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Update workflow (does not update stages)."""
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

        # Return full details
        instance.refresh_from_db()
        response_serializer = LeaveApprovalWorkflowDetailSerializer(instance)

        return Response(
            success=True,
            message="Leave approval workflow updated successfully",
            data=response_serializer.data,
            status_code=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """Delete workflow."""
        instance = self.get_object()
        workflow_name = instance.workflow_name

        # Check if it's the only workflow
        if LeaveApprovalWorkflow.objects.count() == 1:
            return Response(
                success=False,
                errors={'detail': 'Cannot delete the only workflow. At least one workflow must exist.'},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        instance.delete()

        return Response(
            success=True,
            message=f"Leave approval workflow '{workflow_name}' deleted successfully",
            status_code=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def activate(self, request, pk=None):
        """
        Activate a workflow.
        Deactivates all other workflows to ensure only one is active.
        """
        instance = self.get_object()

        # Deactivate all other workflows
        LeaveApprovalWorkflow.objects.exclude(pk=instance.pk).update(is_active=False)

        # Activate this workflow
        instance.is_active = True
        instance.save()

        serializer = LeaveApprovalWorkflowDetailSerializer(instance)
        return Response(
            success=True,
            message=f"Workflow '{instance.workflow_name}' activated successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def add_stage(self, request, pk=None):
        """Add a new stage to the workflow."""
        workflow = self.get_object()
        stage_serializer = LeaveApprovalStageCreateSerializer(data=request.data)

        if not stage_serializer.is_valid():
            return Response(
                success=False,
                errors=stage_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Check if stage_order already exists
        stage_order = stage_serializer.validated_data.get('stage_order')
        if LeaveApprovalStage.objects.filter(workflow=workflow, stage_order=stage_order).exists():
            return Response(
                success=False,
                errors={'stage_order': f'Stage with order {stage_order} already exists in this workflow'},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        stage = stage_serializer.save(workflow=workflow)

        # Return updated workflow with all stages
        workflow.refresh_from_db()
        workflow_serializer = LeaveApprovalWorkflowDetailSerializer(workflow)

        return Response(
            success=True,
            message=f"Stage '{stage.stage_name}' added to workflow successfully",
            data=workflow_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active workflow."""
        active_workflow = LeaveApprovalWorkflow.get_active_workflow()

        if not active_workflow:
            return Response(
                success=False,
                errors={'detail': 'No active workflow found'},
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = LeaveApprovalWorkflowDetailSerializer(active_workflow)
        return Response(
            success=True,
            message="Active workflow retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
