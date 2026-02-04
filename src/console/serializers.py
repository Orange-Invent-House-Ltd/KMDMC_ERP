from rest_framework import serializers
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from audit.serializers import AuditLogSerializer
from user.models.models import Department
from correspondence.models import Correspondence

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_active']
        ref_name = 'UserDepartmentSerializer'
    
    def create(self, validated_data):
        department = Department.objects.create(**validated_data)
        return department
    
class EmptySerializer(serializers.Serializer):
    pass

class FullCorrespondenceRetrieveSerializer(serializers.ModelSerializer):
    """Detailed serializer for retrieving a single correspondence."""
    # parent_audit = AuditLogSerializer(source='child_audit', read_only=True)
    parent_correspondence = serializers.SerializerMethodField()
    reply_notes = serializers.SerializerMethodField()

    class Meta:
        model = Correspondence
        fields = ["parent_audit", "parent_correspondence", "reply_notes", "id", "subject", "type",
            'status', 'priority', 'requires_action',]