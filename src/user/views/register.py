from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from utils.response import Response

from user.serializers.register import RegisterSerializer
from user.serializers.user import UserMinimalSerializer


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                success=False,
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        user_data = UserMinimalSerializer(user).data

        # TODO: Send verification email

        return Response(
            success=True,
            message="User registered successfully.",
            data=user_data,
            status_code=status.HTTP_201_CREATED,
        )
