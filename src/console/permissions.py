from functools import wraps

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_admin
        )


def permissions_required(permissions_list):
    """
    Decorator for view methods that checks if the user has all specified permissions.
    Takes a list of permission strings.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("You must be logged in to access this resource.")
            if request.user.is_authenticated and not request.user.has_permissions(
                permissions_list
            ):
                permission_names = ", ".join(permissions_list)
                raise PermissionDenied(
                    f"You don't have the required permissions: {permission_names}"
                )
            return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator
