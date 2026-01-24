from rest_framework import serializers
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

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