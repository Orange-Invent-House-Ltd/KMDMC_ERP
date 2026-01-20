from django.contrib.auth import get_user_model
from rest_framework import serializers


class UploadMediaSerializer(serializers.Serializer):
    
    images = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )


class DeleteMediaSerializer(serializers.Serializer):
    public_id = serializers.CharField()