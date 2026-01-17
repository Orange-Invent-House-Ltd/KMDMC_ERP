from rest_framework import permissions


class IsHRAdmin(permissions.BasePermission):
    """
    Permission class for HR administrators.
    Allows superadmins and users with HR_CONFIG permissions to manage HR configuration.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Superusers and admins have full access
        if request.user.is_superuser or request.user.is_admin:
            return True

        # Check if user has HR_CONFIG permissions
        # This can be extended to check specific HR-related permissions
        return hasattr(request.user, 'has_permissions') and request.user.has_permissions(['HR_CONFIG'])


class CanViewHRConfig(permissions.BasePermission):
    """
    Permission class for viewing HR configuration.
    All authenticated users can view HR configuration settings.
    """

    def has_permission(self, request, view):
        # All authenticated users can view
        if request.user.is_authenticated:
            # Read-only methods (GET, HEAD, OPTIONS)
            if request.method in permissions.SAFE_METHODS:
                return True

            # Write operations require HR admin permissions
            return request.user.is_superuser or request.user.is_admin or (
                hasattr(request.user, 'has_permissions') and request.user.has_permissions(['HR_CONFIG'])
            )

        return False
