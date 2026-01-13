from django.contrib.auth import get_user_model
from rest_framework import serializers

class UploadMediaSerializer(serializers.Serializer):
    image = serializers.FileField()


class DeleteMediaSerializer(serializers.Serializer):
    public_id = serializers.CharField()