from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from utils.response import Response
from console.permissions import IsSuperAdmin
from hr_config.models import AttendancePolicy
from hr_config.serializers import AttendancePolicySerializer


class AttendancePolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attendance policy (singleton).
    Only one policy instance exists organization-wide.
    Only admins can update, all authenticated users can view.
    """
    queryset = AttendancePolicy.objects.all()
    serializer_class = AttendancePolicySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Only admins can update, all authenticated users can view."""
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated()]

    
    def list(self, request, *args, **kwargs):
        """Return the singleton attendance policy."""
        policy = AttendancePolicy.get_policy()
        serializer = self.get_serializer(policy)

        return Response(
            success=True,
            message="Attendance policy retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve the attendance policy."""
        policy = AttendancePolicy.get_policy()
        serializer = self.get_serializer(policy)

        return Response(
            success=True,
            message="Attendance policy retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    
    def create(self, request, *args, **kwargs):
        """Disabled - only one policy instance is allowed."""
        return Response(
            success=False,
            errors={'detail': 'Cannot create new attendance policy. Only one policy instance is allowed. Please update the existing policy.'},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    
    def update(self, request, *args, **kwargs):
        """Update the attendance policy."""
        partial = kwargs.pop('partial', False)
        policy = AttendancePolicy.get_policy()

        serializer = self.get_serializer(policy, data=request.data, partial=partial, context={'request': request})

        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        # Return updated details
        policy.refresh_from_db()
        response_serializer = self.get_serializer(policy)

        return Response(
            success=True,
            message="Attendance policy updated successfully",
            data=response_serializer.data,
            status_code=status.HTTP_200_OK
        )

    
    def destroy(self, request, *args, **kwargs):
        """Disabled - attendance policy cannot be deleted."""
        return Response(
            success=False,
            errors={'detail': 'Cannot delete attendance policy. The policy is required for organization operations.'},
            status_code=status.HTTP_400_BAD_REQUEST
        )
