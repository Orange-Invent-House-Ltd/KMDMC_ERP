from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from utils.response import Response
from user.serializers.password import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from user import tasks
from utils.utils import (
    generate_otp,
    generate_random_text,
)
from core.resources.cache import Cache


class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        user = serializer.validated_data["user"]
        name = user.name
        otp = generate_otp()
        otp_key = generate_random_text(80)

        value = {
            "otp": otp,
            "email": email,
            "is_valid": True,
        }
        with Cache() as cache:
            cache.set(otp_key, value, 60 * 15)  # OTP/Token expires in 15 minutes
        dynamic_values = {
            "first_name": name.split(" ")[0],
            "recipient": email,
            "otp": otp,
        }
        # TODO: Uncomment when email task is ready
        # tasks.send_reset_password_request_email.delay(email, dynamic_values)l

        return Response(
            success=True,
            message="If an account exists with this email, you will receive a password reset link.",
            data={"otp_key": otp_key}, #remove this in production
            status_code=status.HTTP_200_OK,
        )
    

class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        user = serializer.validated_data["user"]
        user.set_password(new_password)
        user.save()

        return Response(
            success=True,
            message="Password has been reset successfully. Please sign in with your new password.",
            status_code=status.HTTP_200_OK,
        )


class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        return Response(
            success=True,
            message="Password changed successfully.",
        )