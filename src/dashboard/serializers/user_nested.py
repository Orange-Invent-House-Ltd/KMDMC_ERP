from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RequesterSerializer(serializers.ModelSerializer):
    initials = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'initials']

    def get_initials(self, obj):
        if obj.name:
            parts = obj.name.split()
            return ''.join([p[0].upper() for p in parts[:2]])
        return obj.email[0].upper() if obj.email else 'U'
