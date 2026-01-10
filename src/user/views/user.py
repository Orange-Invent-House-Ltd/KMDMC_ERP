from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from utils.response import Response 

from user.models import CustomUser
from user.serializers.user import UserUpdateSerializer, LogoutSerializer


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response(
                {
                    "success": True,
                    "message": "Logged out successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {
                    "success": True,
                    "message": "Logged out successfully.",
                },
                status=status.HTTP_200_OK,
            )



class UserUpdateView(UpdateAPIView):
    """
    Admin endpoint to update any user by ID.
    
    PUT/PATCH /v1/auth/users/<user_id>/
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    lookup_url_kwarg = 'user_id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return Response(
                success = False,
                message = "Validation error",
                errors = serializer.errors,
                status_code = status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response(
            success = True,
            message = "User updated successfully",
            data = serializer.data,
            status_code = status.HTTP_200_OK,
        )
