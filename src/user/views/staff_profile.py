from rest_framework import status, generics
from utils.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from user.serializers.staff_profile import (
    StaffProfileSerializer,
    StaffCorrespondenceSerializer,
)

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
