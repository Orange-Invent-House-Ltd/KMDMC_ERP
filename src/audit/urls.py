from django.urls import include, path
from rest_framework.routers import DefaultRouter

from audit.views import AuditLogViewSets

app_name = "audit"

router = DefaultRouter()
router.register("", AuditLogViewSets, basename="audit")

urlpatterns = [
    path("", include(router.urls)),
]
