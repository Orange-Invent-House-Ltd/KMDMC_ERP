from rest_framework import serializers
from dashboard.models import DepartmentPerformance, Department
from .department import DepartmentSerializer


class DepartmentPerformanceSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = DepartmentPerformance
        fields = [
            'id', 'department', 'department_id', 'department_name', 
            'month', 'performance_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
