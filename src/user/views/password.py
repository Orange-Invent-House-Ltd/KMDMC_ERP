from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.models import CustomUser
from user.serializers.password import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]

        # TODO: Generate reset token and send email
        # For security, always return success message regardless of email existence

        return Response(
            {
                "success": True,
                "message": "If an account exists with this email, you will receive a password reset link.",
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        # TODO: Validate token and get user
        # TODO: Set new password

        return Response(
            {
                "success": True,
                "message": "Password has been reset successfully. Please sign in with your new password.",
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        return Response(
            {
                "success": True,
                "message": "Password changed successfully.",
            },
            status=status.HTTP_200_OK,
        )
