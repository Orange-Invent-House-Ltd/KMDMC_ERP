from rest_framework import serializers
from django.contrib.auth import get_user_model

from dashboard.models import Approval
from .user_nested import RequesterSerializer


class DashboardSerializer(serializers.ModelSerializer):
    requester = RequesterSerializer(read_only=True)

    class Meta:
        model = Approval
        fields = [
            "id",
            "requester",
            "status",
            "created_at",
            "updated_at",
        ]