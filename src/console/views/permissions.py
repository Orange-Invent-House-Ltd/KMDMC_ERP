from django.utils import timezone
from django_filters import rest_framework as django_filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from console.permissions import IsSuperAdmin
from user.filters import PermissionFilter, RoleFilter
from user.models.admin import Permission, Role
from user.serializers.permissions import PermissionSerializer, RoleSerializer
from utils.pagination import CustomPagination
from utils.response import Response
from console.permissions import permissions_required
from utils.permissions import PERMISSIONS


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().order_by("module", "name", "-created_at")
    serializer_class = PermissionSerializer
    allowed_methods = ["get", "post", "patch", "delete"]
    permission_classes = [IsSuperAdmin]
    pagination_class = CustomPagination
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description", "module"]
    filterset_class = PermissionFilter

    @swagger_auto_schema(
        operation_description="List all permissions by filter",
        responses={
            200: PermissionSerializer,
        },
    )
    
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        qs = self.paginate_queryset(queryset)
        serializer = self.get_serializer(qs, many=True)
        self.pagination_class.message = "Permissions retrieved successfully"
        response = self.get_paginated_response(
            serializer.data,
        )
        return response

    @swagger_auto_schema(
        operation_description="Retrieve a permission",
        responses={200: PermissionSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Permission retrieved",
            status_code=status.HTTP_200_OK,
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_description="Create a new permission",
        request_body=PermissionSerializer,
        responses={
            201: PermissionSerializer,
        },
    )

    @permissions_required([PERMISSIONS.CAN_ADD_PERMISSIONS_TO_ROLE])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)
        return Response(
            success=True,
            message="Permission created",
            status_code=status.HTTP_201_CREATED,
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_description="Update a permission",
        request_body=PermissionSerializer,
        responses={
            200: PermissionSerializer,
        },
    )

    @permissions_required([PERMISSIONS.CAN_UPDATE_PERMISSIONS])
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_update(serializer)
        return Response(
            success=True,
            message="Permission updated",
            status_code=status.HTTP_200_OK,
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_description="Delete a permission",
        responses={204: "No content"},
    )

    @permissions_required([PERMISSIONS.CAN_DELETE_PERMISSIONS])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            success=True,
            message="Permission deleted",
            status_code=status.HTTP_204_NO_CONTENT,
        )


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by("name", "-created_at")
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]
    filterset_class = RoleFilter

    @swagger_auto_schema(
        operation_description="List all roles by filter",
        responses={
            200: RoleSerializer,
        },
    )
    
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        qs = self.paginate_queryset(queryset)
        serializer = self.get_serializer(qs, many=True)
        self.pagination_class.message = "Roles retrieved successfully"
        response = self.get_paginated_response(
            serializer.data,
        )
        return response

    @swagger_auto_schema(
        operation_description="Retrieve a role",
        responses={200: RoleSerializer},
    )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Role retrieved",
            status_code=status.HTTP_200_OK,
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_description="Create a new role",
        request_body=RoleSerializer,
        responses={
            201: RoleSerializer,
        },
    )
    @permissions_required([PERMISSIONS.CAN_ADD_ROLES])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)
        return Response(
            success=True,
            message="Role created",
            status_code=status.HTTP_201_CREATED,
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_description="Update a role",
        request_body=RoleSerializer,
        responses={
            200: RoleSerializer,
        },
    )
    @permissions_required([PERMISSIONS.CAN_UPDATE_ROLES])
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                success=False,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_update(serializer)
        return Response(
            success=True,
            message="Role updated",
            status_code=status.HTTP_200_OK,
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_description="Delete a role",
        responses={204: "No content"},
    )
    @permissions_required([PERMISSIONS.CAN_DELETE_ROLES])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if role is assigned to any users before deleting
        if instance.users.exists():
            return Response(
                success=False,
                message="Cannot delete role as it is assigned to users",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(
            success=True,
            message="Role deleted",
            status_code=status.HTTP_204_NO_CONTENT,
        )

    @swagger_auto_schema(
        operation_description="Add permissions to a role",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "permission_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description="List of permission IDs to add",
                )
            },
        ),
        responses={200: RoleSerializer},
    )
    @permissions_required([PERMISSIONS.CAN_ADD_PERMISSIONS_TO_ROLE])
    @action(detail=True, methods=["post"], url_path="add-permissions")
    def add_permissions(self, request, pk=None):
        role = self.get_object()
        permission_ids = request.data.get("permission_ids", [])
        if not permission_ids:
            return Response(
                success=False,
                message="No permission IDs provided",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        permissions_to_add = Permission.objects.filter(id__in=permission_ids)
        if len(permissions_to_add) != len(permission_ids):
            return Response(
                success=False,
                message="Some permission IDs are invalid",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        role.permissions.add(*permissions_to_add)
        serializer = self.get_serializer(role)
        return Response(
            success=True,
            message="Permissions added to role",
            status_code=status.HTTP_200_OK,
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_description="Remove permissions from a role",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "permission_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description="List of permission IDs to remove",
                )
            },
        ),
        responses={200: RoleSerializer},
    )
    @permissions_required([PERMISSIONS.CAN_ADD_PERMISSIONS_TO_ROLE])
    @action(detail=True, methods=["post"], url_path="remove-permissions")
    def remove_permissions(self, request, pk=None):
        role = self.get_object()
        permission_ids = request.data.get("permission_ids", [])
        if not permission_ids:
            return Response(
                success=False,
                message="No permission IDs provided",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Get permissions that exist
        permissions_to_remove = Permission.objects.filter(id__in=permission_ids)
        if len(permissions_to_remove) != len(permission_ids):
            return Response(
                success=False,
                message="Some permission IDs are invalid",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        role.permissions.remove(*permissions_to_remove)
        serializer = self.get_serializer(role)
        return Response(
            success=True,
            message="Permissions removed from role",
            status_code=status.HTTP_200_OK,
            data=serializer.data,
        )
