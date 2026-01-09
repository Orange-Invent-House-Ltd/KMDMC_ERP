from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ApprovalViewSet,
    TaskViewSet,
)

app_name = 'dashboard'

router = DefaultRouter()
router.register(r'approvals', ApprovalViewSet, basename='approval')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls))
]
