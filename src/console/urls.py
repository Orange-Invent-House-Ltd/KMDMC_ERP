from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views.user import MDVerifyUserView


from console.views import (
    DepartmentViewSet,
    StaffsProfileViewSet
    )

app_name = "console"

# Router for ViewSets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'staff', StaffsProfileViewSet, basename='staff')

urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
    path("MDVerify/<int:user_id>/", MDVerifyUserView.as_view(), name="MD_verify_user"),
]
