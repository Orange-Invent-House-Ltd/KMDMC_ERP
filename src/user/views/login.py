from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from utils.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from audit.enums import AuditModuleEnum, AuditStatusEnum, AuditTypeEnum, LogParams
from user.serializers.login import LoginSerializer
from user.serializers.user import UserMinimalSerializer


class LoginView(GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

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
        event = LogParams(
            audit_type=AuditTypeEnum.USER_LOGIN.raw_value,
            audit_module=AuditModuleEnum.USER.raw_value,
            status=AuditStatusEnum.SUCCESS.raw_value,
            user_id=str(request.user.id),
            user_name=request.user.name.upper(),
            user_email=request.user.email,
            user_role=request.user.role,
            action=f"{request.user.name.upper()} logged in",
            request_meta=extract_api_request_metadata(request),
        )
        log_audit_event_task.delay(event.__dict__)

        return Response(
            success=True,
            message=f"Welcome back, {user.name}!",
            data={
                "token": str(refresh.access_token),
                "user": user_data,
            },
            status_code=status.HTTP_200_OK,
        )
