from django.urls import path, include
from rest_framework.routers import DefaultRouter

from console.views import (
    DepartmentViewSet,
    StaffsProfileViewSet,
    StaffTaskViewSet,
)

app_name = "console"

# Router for ViewSets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'staff', StaffsProfileViewSet, basename='staff')
router.register(r'tasks', StaffTaskViewSet, basename='task')

urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
]
