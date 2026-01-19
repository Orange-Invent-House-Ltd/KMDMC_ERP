from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from rest_framework import filters

from utils.response import Response
from utils.pagination import CustomPagination
from console.permissions import IsSuperAdmin
from hr_config.models import PublicHoliday
from hr_config.serializers import (
    PublicHolidayListSerializer,
    PublicHolidayDetailSerializer,
    PublicHolidayCreateSerializer,
    PublicHolidayUpdateSerializer,
)


class PublicHolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing public holidays.
    HR admins can manage, all staff can view.
    """
    queryset = PublicHoliday.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['year', 'holiday_type', 'is_recurring']
    search_fields = ['holiday_name']
    ordering_fields = ['date', 'holiday_name', 'created_at']
    ordering = ['date']

    def get_serializer_class(self):
        if self.action == 'list':
            return PublicHolidayListSerializer
        elif self.action == 'retrieve':
            return PublicHolidayDetailSerializer
        elif self.action == 'create':
            return PublicHolidayCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PublicHolidayUpdateSerializer
        return PublicHolidayListSerializer

    def get_permissions(self):
        """Only admins can create/update/delete, all authenticated users can view."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """List all public holidays."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            message="Public holidays retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve single public holiday."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Public holiday retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        """Create new public holiday."""
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        # Return full details
        holiday = PublicHoliday.objects.get(pk=serializer.instance.pk)
        response_serializer = PublicHolidayDetailSerializer(holiday)

        return Response(
            success=True,
            message="Public holiday created successfully",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Update public holiday."""
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
        response_serializer = PublicHolidayDetailSerializer(instance)

        return Response(
            success=True,
            message="Public holiday updated successfully",
            data=response_serializer.data,
            status_code=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """Delete public holiday."""
        instance = self.get_object()
        holiday_name = instance.holiday_name
        instance.delete()

        return Response(
            success=True,
            message=f"Public holiday '{holiday_name}' deleted successfully",
            status_code=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def by_year(self, request):
        """Get holidays by specific year."""
        year = request.query_params.get('year')

        if not year:
            return Response(
                success=False,
                errors={'year': 'Year parameter is required'},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            year = int(year)
        except ValueError:
            return Response(
                success=False,
                errors={'year': 'Year must be a valid integer'},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(year=year).order_by('date')
        serializer = PublicHolidayListSerializer(queryset, many=True)

        return Response(
            success=True,
            message=f"Holidays for year {year} retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
