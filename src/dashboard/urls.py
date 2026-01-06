from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DepartmentViewSet,
    ApprovalViewSet,
    TaskViewSet,
    CorrespondenceViewSet,
    MemoViewSet,
    DashboardView,
)

app_name = 'dashboard'

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'approvals', ApprovalViewSet, basename='approval')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'correspondence', CorrespondenceViewSet, basename='correspondence')
router.register(r'memos', MemoViewSet, basename='memo')

urlpatterns = [
    path('', include(router.urls)),
    path('overview/', DashboardView.as_view(), name='dashboard-overview'),
]
