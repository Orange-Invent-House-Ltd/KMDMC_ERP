from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from rest_framework import filters

from utils.response import Response
from utils.pagination import CustomPagination
from console.permissions import IsSuperAdmin
from hr_config.models import AppraisalTemplate
from hr_config.serializers import (
    AppraisalTemplateListSerializer,
    AppraisalTemplateDetailSerializer,
    AppraisalTemplateCreateSerializer,
    AppraisalTemplateUpdateSerializer,
)


class AppraisalTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appraisal templates.
    Only HR admins/superadmins can manage templates.
    """
    queryset = AppraisalTemplate.objects.select_related('created_by').all()
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    pagination_class = CustomPagination

    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['status']
    search_fields = ['template_name', 'template_id', 'description']
    ordering_fields = ['created_at', 'updated_at', 'template_name']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return AppraisalTemplateListSerializer
        elif self.action == 'retrieve':
            return AppraisalTemplateDetailSerializer
        elif self.action == 'create':
            return AppraisalTemplateCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AppraisalTemplateUpdateSerializer
        return AppraisalTemplateListSerializer

    def list(self, request, *args, **kwargs):
        """List all appraisal templates."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            message="Appraisal templates retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve single appraisal template."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Appraisal template retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        """Create new appraisal template."""
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        # Return full details
        template = AppraisalTemplate.objects.select_related('created_by').get(
            pk=serializer.instance.pk
        )
        response_serializer = AppraisalTemplateDetailSerializer(template)

        return Response(
            success=True,
            message="Appraisal template created successfully",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Update appraisal template."""
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
        response_serializer = AppraisalTemplateDetailSerializer(instance)

        return Response(
            success=True,
            message="Appraisal template updated successfully",
            data=response_serializer.data,
            status_code=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """Delete appraisal template."""
        instance = self.get_object()
        template_name = instance.template_name
        instance.delete()

        return Response(
            success=True,
            message=f"Appraisal template '{template_name}' deleted successfully",
            status_code=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive an appraisal template."""
        instance = self.get_object()
        instance.status = 'archived'
        instance.save()

        serializer = AppraisalTemplateDetailSerializer(instance)
        return Response(
            success=True,
            message="Appraisal template archived successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an appraisal template."""
        instance = self.get_object()
        instance.status = 'active'
        instance.save()

        serializer = AppraisalTemplateDetailSerializer(instance)
        return Response(
            success=True,
            message="Appraisal template activated successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
