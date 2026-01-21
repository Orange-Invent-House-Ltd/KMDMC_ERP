from common.views.upload import DeleteMediaView, UploadMediaView
from django.urls import path, include

app_name = "common"

urlpatterns = [
    path("upload", UploadMediaView.as_view(), name="upload-media"),
    path("uploads/delete", DeleteMediaView.as_view(), name="delete-media"),
]