from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views.user import MDVerifyUserView

from console.views.permissions import PermissionViewSet, RoleViewSet
from console.views.views import (
    DepartmentViewSet,
    StaffsProfileViewSet,
    UserDropdownListView
    )

app_name = "console"

# Router for ViewSets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'staff', StaffsProfileViewSet, basename='staff')
router.register(r"permissions", PermissionViewSet, basename="permissions")
router.register(r"roles", RoleViewSet, basename="roles")

urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
    path("MDVerify/<int:user_id>/", MDVerifyUserView.as_view(), name="MD_approve_user"),
    path("user-dropdown/", UserDropdownListView.as_view(), name="user_dropdown"),
]
