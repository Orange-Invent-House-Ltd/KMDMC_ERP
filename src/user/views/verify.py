from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from utils.response import Response

from user.models import CustomUser
from user.serializers.user import UserMinimalSerializer


class VerifyUserView(APIView):
    """Endpoint to verify a user's email/account."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """
        Verify a user by email or user_id.
        
        Request body:
        {
            "email": "user@example.com"  # or "user_id": 123
        }
        """
        email = request.data.get("email")
        user_id = request.data.get("user_id")

        if not email and not user_id:
            return Response(
                success=False,
                message="Email or user_id is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if email:
                user = CustomUser.objects.get(email=email)
            else:
                user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                success=False,
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if user.is_verified:
            return Response(
                success=False,
                message="User is already verified",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        user_data = UserMinimalSerializer(user).data

        return Response(
            success=True,
            message="User verified successfully",
            data=user_data,
            status_code=status.HTTP_200_OK,
        )

