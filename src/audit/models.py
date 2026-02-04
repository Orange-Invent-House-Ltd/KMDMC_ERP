import uuid

from django.db import models

from .enums import AuditModuleEnum, AuditStatusEnum, AuditTypeEnum, LogParams
from correspondence.models import Correspondence


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit_module = models.CharField(
        max_length=50, choices=AuditModuleEnum.choices(), db_index=True
    )
    correspondence = models.ForeignKey(
        Correspondence, null=True, blank=True, on_delete=models.CASCADE, related_name="audit_logs"
    )
    audit_type = models.CharField(
        max_length=100, choices=AuditTypeEnum.choices(), db_index=True
    )
    status = models.CharField(
        max_length=10, choices=AuditStatusEnum.choices(), db_index=True
    )
    user_id = models.CharField(max_length=255, db_index=True)
    user_name = models.CharField(max_length=255)
    user_role = models.CharField(max_length=255)
    user_email = models.EmailField(db_index=True)

    action = models.TextField()
    request_meta = models.JSONField(null=True, blank=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text="Unique request ID to trace log entries across systems/logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_name} <{self.user_email}> - {self.action}"

    @classmethod
    def log_action(cls, params: LogParams):
        """
        Convenience method to log audit actions using LogParams dataclass
        """
        return cls.objects.create(
            audit_module=params.audit_module,
            audit_type=params.audit_type,
            status=params.status,
            user_id=params.user_id,
            user_name=params.user_name,
            user_role=params.user_role,
            user_email=params.user_email,
            action=params.action,
            correspondence_id=params.correspondence_id,
            request_meta=params.request_meta,
            old_values=params.old_values,
            new_values=params.new_values,
            request_id=params.request_id,
        )
