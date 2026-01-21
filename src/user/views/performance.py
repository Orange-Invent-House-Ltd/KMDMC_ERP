from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from utils.response import Response
from user.serializers.login import LoginSerializer
from user.serializers.user import UserMinimalSerializer, PerformanceOverviewSerializer


class PerformanceOverviewView(GenericAPIView):

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PerformanceOverviewSerializer

    def get(self, request):
        # Placeholder logic for performance overview
        # data = {
        #     "total_employees": 150,
        #     "active_projects": 25,
        #     "completed_tasks": 1200,
        #     "pending_approvals": 45,
        # }

        return Response(
            success=True,
            message="Performance overview fetched successfully.",
            data=data,
            status_code=status.HTTP_200_OK,
        )