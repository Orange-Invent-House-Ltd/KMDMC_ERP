from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="KMDMC ERP API",
        default_version="v1",
        description="KMDMC ERP System API Documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=None,
)

urlpatterns = [
    path("", views.api_ok, name="api-ok"),
    path("admin/", admin.site.urls),
    path("v1/health-check/", views.HealthCheckView.as_view(), name="health-check"),
    path("swaggerxyz-docs", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-schema-ui"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-schema-ui"),
    path("v1/auth/", include("user.urls", namespace="user")),
    path("v1/console/", include("console.urls", namespace="console")),
    path("v1/correspondence/", include("correspondence.urls", namespace="correspondence")),
    path("v1/tasks/", include("tasks.urls", namespace="tasks")),
    path("v1/common/", include("common.urls", namespace="common")),
    path("v1/hr-config/", include("hr_config.urls", namespace="hr_config")),
    path("v1/audit/" , include("audit.urls", namespace="audit")),
]
