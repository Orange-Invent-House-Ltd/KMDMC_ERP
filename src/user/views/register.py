from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from user.serializers.register import RegisterSerializer
from user.serializers.user import UserMinimalSerializer


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        
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

        user = serializer.save()
        user_data = UserMinimalSerializer(user).data

        # TODO: Send verification email

        return Response(
            {
                "success": True,
                "message": "Account created successfully! Please check your email to verify your account.",
                "data": {
                    "user": user_data,
                },
            },
            status=status.HTTP_201_CREATED,
        )
