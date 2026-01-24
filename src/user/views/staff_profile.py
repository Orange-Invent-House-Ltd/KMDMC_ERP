from rest_framework import status, generics
from utils.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from user.serializers.staff_profile import (
    StaffProfileSerializer,
    StaffCorrespondenceSerializer,
)
from user.serializers.user import PerformanceOverviewSerializer
from user.models.models import PerformanceRecord

class StaffProfileView(APIView):
    """View for current user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user's profile."""
        serializer = StaffProfileSerializer(request.user, context={'request': request})
        
        return Response(
            success=True,
            message="Profile retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

class PerformanceOverviewView(generics.GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PerformanceOverviewSerializer

    def get(self, request):
        """Retrieve performance overview data."""
        queryset = PerformanceRecord.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            message="Performance overview fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )