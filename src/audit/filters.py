import django_filters

from audit.enums import AuditModuleEnum, AuditStatusEnum, AuditTypeEnum
from audit.models import AuditLog
from common.filters import DateFilter


class AuditLogFilter(DateFilter):
    audit_module = django_filters.ChoiceFilter(choices=AuditModuleEnum.choices())
    audit_type = django_filters.ChoiceFilter(choices=AuditTypeEnum.choices())
    status = django_filters.ChoiceFilter(choices=AuditStatusEnum.choices())
    user_name = django_filters.CharFilter(lookup_expr="icontains")
    user_email = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = AuditLog
        fields = [
            "audit_module",
            "audit_type",
            "status",
            "user_name",
            "user_email",
            "start",
            "end",
        ]
