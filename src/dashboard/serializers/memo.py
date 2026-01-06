from rest_framework import serializers
from django.contrib.auth import get_user_model

from dashboard.models import Memo, Department
from .department import DepartmentSerializer
from .user_nested import RequesterSerializer

User = get_user_model()


class MemoSerializer(serializers.ModelSerializer):
    author = RequesterSerializer(read_only=True)
    recipients = RequesterSerializer(many=True, read_only=True)
    recipient_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='recipients',
        write_only=True,
        many=True,
        required=False
    )
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Memo
        fields = [
            'id', 'title', 'content', 'author', 'recipients', 'recipient_ids',
            'department', 'department_id', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        recipients = validated_data.pop('recipients', [])
        validated_data['author'] = self.context['request'].user
        memo = Memo.objects.create(**validated_data)
        if recipients:
            memo.recipients.set(recipients)
        return memo

    def update(self, instance, validated_data):
        recipients = validated_data.pop('recipients', None)
        instance = super().update(instance, validated_data)
        if recipients is not None:
            instance.recipients.set(recipients)
        return instance
