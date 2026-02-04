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
    HR_CONFIG = "hr_config", "HR Configuration"
    TASKS = "tasks", "Tasks Management"
    CORRESPONDENCE = "correspondence", "Correspondence Management"


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
    CHANGE_CORRESPONDENCE_STATUS = "change_correspondence_status", "Changed Correspondence Status"
    ARCHIVE_CORRESPONDENCE = "archive_correspondence", "Archived Correspondence"

    # HR Configuration
    CREATE_APPRAISAL_TEMPLATE = "create_appraisal_template", "Created Appraisal Template"
    UPDATE_APPRAISAL_TEMPLATE = "update_appraisal_template", "Updated Appraisal Template"
    ARCHIVE_APPRAISAL_TEMPLATE = "archive_appraisal_template", "Archived Appraisal Template"
    DELETE_APPRAISAL_TEMPLATE = "delete_appraisal_template", "Deleted Appraisal Template"
    CREATE_LEAVE_TYPE = "create_leave_type", "Created Leave Type"
    UPDATE_LEAVE_TYPE = "update_leave_type", "Updated Leave Type"
    DELETE_LEAVE_TYPE = "delete_leave_type", "Deleted Leave Type"
    CREATE_PUBLIC_HOLIDAY = "create_public_holiday", "Created Public Holiday"
    UPDATE_PUBLIC_HOLIDAY = "update_public_holiday", "Updated Public Holiday"
    DELETE_PUBLIC_HOLIDAY = "delete_public_holiday", "Deleted Public Holiday"
    UPDATE_ATTENDANCE_POLICY = "update_attendance_policy", "Updated Attendance Policy"
    CREATE_LEAVE_WORKFLOW = "create_leave_workflow", "Created Leave Approval Workflow"
    UPDATE_LEAVE_WORKFLOW = "update_leave_workflow", "Updated Leave Approval Workflow"
    DELETE_LEAVE_WORKFLOW = "delete_leave_workflow", "Deleted Leave Approval Workflow"
    ACTIVATE_LEAVE_WORKFLOW = "activate_leave_workflow", "Activated Leave Approval Workflow"

    # TASKS
    CREATE_TASK = "create_task", "Created Task"
    UPDATE_TASK = "update_task", "Updated Task"
    DELETE_TASK = "delete_task", "Deleted Task"
    ASSIGN_TASK = "assign_task", "Assigned Task"

    # CORRESPONDENCE
    CREATE_CORRESPONDENCE = "create_correspondence", "Created Correspondence"
    UPDATE_CORRESPONDENCE = "update_correspondence", "Updated Correspondence"
    DELETE_CORRESPONDENCE = "delete_correspondence", "Deleted Correspondence"
    VIEW_CORRESPONDENCE = "view_correspondence", "Viewed Correspondence"


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
    correspondence_id: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
