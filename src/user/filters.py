import django_filters
from django_filters.rest_framework import FilterSet

from user.models.admin import Permission, Role


class PermissionFilter(FilterSet):
    module = django_filters.CharFilter(lookup_expr="exact")
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Permission
        fields = ["module", "name"]


class RoleFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    parent = django_filters.NumberFilter(field_name="parent__id")

    class Meta:
        model = Role
        fields = ["name", "parent"]

