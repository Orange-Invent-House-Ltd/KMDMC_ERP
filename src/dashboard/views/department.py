from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from dashboard.models import Department
from dashboard.serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
