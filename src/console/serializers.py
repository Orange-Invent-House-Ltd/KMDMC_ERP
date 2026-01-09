from rest_framework import serializers
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from user.models import (CustomUser, Department, StaffActivity,
                         PerformanceRecord, StaffTask)
from correspondence.models import Correspondence

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'is_active']
        ref_name = 'UserDepartmentSerializer'
    
    def create(self, validated_data):
        department = Department.objects.create(**validated_data)
        return department