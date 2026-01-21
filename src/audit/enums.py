from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum


class CustomEnum(Enum):
    @classmethod
    def values(cls):
        return [c.raw_value for c in cls]

    @classmethod
    def choices(cls):
        return [(c.raw_value, c.label) for c in cls]

    @property
    def raw_value(self):
        return self.value if not isinstance(self.value, tuple) else self.value[0]

    @property
    def label(self):
        return self.value if not isinstance(self.value, tuple) else self.value[1]


class AuditStatusEnum(CustomEnum):
    SUCCESS = "success", "Success"
    FAILURE = "failure", "Failure"
    PENDING = "pending", "Pending"


class AuditModuleEnum(CustomEnum):
    AUTH = "auth", "Authentication"
    USER = "user", "User Management"
    AUDIT = "audit", "Audit Trail" 
    

class AuditTypeEnum(CustomEnum):
    # Auth
    ADMIN_LOGIN = "admin_login", "Admin Login"

    # User Management
    USER_LOGIN = "user", "User"
    DEACTIVATE_USER = "deactivate_user", "Deactivated User"
    APPROVE_USER = "approve_user", "Approved User"
    RESTRICT_USER = "restrict_user", "Restricted User"
    UNRESTRICT_USER = "unrestrict_user", "Unrestricted User"
    REMOVE_ADMIN_USER = "remove_admin_user", "Removed Admin User"
    UPDATE_ADMIN_USER = "update_admin_user", "Updated Admin User"
    MANUAL_DEBIT_USER = "manual_debit_user", "Manually Debited User"
    MANUAL_CREDIT_USER = "manual_credit_user", "Manually Credited User"
    CONVERT_USER_TYPE = "convert_user_type", "Converted User Type"
    VIEW_CORRESPONDENCE = "view_correspondence", "Viewed Correspondence"
    CHANGE_CORRESPONDENCE_STATUS = "change_correspondence_status", "Changed Correspondence Status"
    ARCHIVE_CORRESPONDENCE = "archive_correspondence", "Archived Correspondence"

    

    

@dataclass
class LogParams:
    audit_module: AuditModuleEnum
    audit_type: AuditTypeEnum
    status: AuditStatusEnum
    user_id: str
    user_name: str
    user_role: str
    user_email: str
    action: str
    request_meta: dict
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
