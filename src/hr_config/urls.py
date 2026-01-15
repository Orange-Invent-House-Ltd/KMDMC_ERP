from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hr_config.views import (
    AppraisalTemplateViewSet,
    LeaveTypeViewSet,
    PublicHolidayViewSet,
    AttendancePolicyViewSet,
    LeaveApprovalWorkflowViewSet,
)

app_name = 'hr_config'

router = DefaultRouter()
router.register(r'appraisal-templates', AppraisalTemplateViewSet, basename='appraisal-template')
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'public-holidays', PublicHolidayViewSet, basename='public-holiday')
router.register(r'attendance-policy', AttendancePolicyViewSet, basename='attendance-policy')
router.register(r'leave-approval-workflows', LeaveApprovalWorkflowViewSet, basename='leave-approval-workflow')

urlpatterns = [
    path('', include(router.urls)),
]
