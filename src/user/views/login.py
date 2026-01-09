from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from utils.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from user.serializers.login import LoginSerializer
from user.serializers.user import UserMinimalSerializer


class LoginView(GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []  # Disable authentication for login endpoint

    def post(self, request):
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]
        remember_me = serializer.validated_data.get("remember_me", False)

        refresh = RefreshToken.for_user(user)
        
        if remember_me:
            refresh.set_exp(lifetime=30 * 24 * 60 * 60)

        user_data = UserMinimalSerializer(user).data

        return Response(
            success=True,
            message=f"Welcome back, {user.name}!",
            data={
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
            },
            status_code=status.HTTP_200_OK,
        )
