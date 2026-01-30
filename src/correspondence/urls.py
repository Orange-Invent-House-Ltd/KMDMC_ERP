from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CorrespondenceViewSet, CorrespondenceDelegateViewSet
)

app_name = 'correspondence'

router = DefaultRouter()

# Main correspondence endpoints
router.register(r'delegates', CorrespondenceDelegateViewSet, basename='correspondence-delegate')
router.register(r'', CorrespondenceViewSet, basename='correspondence')



# Supporting entity endpoints
urlpatterns = [
    path('', include(router.urls)),
]
