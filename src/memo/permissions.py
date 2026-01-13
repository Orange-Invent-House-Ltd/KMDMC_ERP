from rest_framework import permissions


class MemoPermissions(permissions.BasePermission):
    """
    Custom permissions for memo operations.

    - Any authenticated user can create memos
    - Only initiator can edit/cancel draft memos
    - Unit Head can approve/reject at stage 2
    - Director/MD can approve/reject at stage 3
    """

    def has_permission(self, request, view):
        """Check if user has general permission to access memo endpoints."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions."""
        user = request.user

        # Read permissions
        if view.action in ['retrieve', 'list']:
            # Can view if: initiator, unit head, CC'd, or approver
            return (
                user == obj.initiator or
                user == obj.to_unit_head or
                user == obj.through_cc or
                user == obj.final_approver or
                user.role in ['super_admin', 'director']
            )

        # Update/Delete permissions (only for drafts)
        if view.action in ['update', 'partial_update', 'destroy', 'cancel']:
            return user == obj.initiator and obj.status == 'draft'

        # Approval permissions
        if view.action == 'approve':
            if obj.current_stage == 2:
                return user == obj.to_unit_head
            elif obj.current_stage == 3:
                return user == obj.final_approver
            return False

        # Rejection permissions
        if view.action == 'reject':
            return user in [obj.to_unit_head, obj.final_approver]

        # Submit permissions
        if view.action == 'submit_for_approval':
            return user == obj.initiator and obj.status == 'draft'

        return False
