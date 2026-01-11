from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from utils.response import Response 
from audit.enums import AuditModuleEnum, AuditStatusEnum, AuditTypeEnum, LogParams
from audit.tasks import log_audit_event_task
from user.models import CustomUser
from user.serializers.user import UserUpdateSerializer, LogoutSerializer
from utils.activity_log import extract_api_request_metadata

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



class MDVerifyUserView(UpdateAPIView):
    """
    Admin endpoint to update any user by ID.
    """
    http_method_names = ['patch']
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_url_kwarg = 'user_id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Check if already verified
        if instance.is_verified:
            return Response(
                success=False,
                message="User is already verified.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return Response(
                success = False,
                message = "Validation error",
                errors = serializer.errors,
                status_code = status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        # event = LogParams(
        #     audit_type=AuditTypeEnum.APPROVE_USER.raw_value,
        #     audit_module=AuditModuleEnum.AUDIT.raw_value,
        #     status=AuditStatusEnum.SUCCESS.raw_value,
        #     user_id=str(request.user.id),
        #     user_name=request.user.name.upper(),
        #     user_email=request.user.email,
        #     user_role = request.user.role,
        #     action=f"{request.user.name.upper()} approved user {instance.name.upper()}",
        #     request_meta=extract_api_request_metadata(request),
        # )
        # log_audit_event_task.delay(event.__dict__)

        return Response(
            success = True,
            message = "User updated successfully",
            data = serializer.data,
            status_code = status.HTTP_200_OK,
        )
