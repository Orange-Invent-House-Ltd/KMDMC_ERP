from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ApprovalViewSet

app_name = 'dashboard'

router = DefaultRouter()
router.register(r'approvals', ApprovalViewSet, basename='approval')

urlpatterns = [
    path('', include(router.urls))
]
