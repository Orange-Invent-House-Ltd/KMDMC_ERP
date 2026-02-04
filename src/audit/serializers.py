from rest_framework import serializers

from audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    ip_address = serializers.SerializerMethodField()
    class Meta:
        model = AuditLog
        fields = ["user_name", "correspondence", "user_role", "action", "audit_type", "audit_module",
                  "ip_address", "created_at", ]
        
    def get_ip_address(self, obj):
        if not obj.request_meta:
            return None
        return obj.request_meta.get('ip_address')
    