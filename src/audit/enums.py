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
    MEMO = "memo", "Memo Management" 
    

class AuditTypeEnum(CustomEnum):
    # Auth
    ADMIN_LOGIN = "admin_login", "Admin Login"

    # User Management
    INVITE_USER = "invite_user", "Invited User"
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

    # Memo actions
    CREATE_MEMO = "create_memo", "Created Memo"
    EDIT_MEMO = "edit_memo", "Edited Memo"
    SUBMIT_MEMO = "submit_memo", "Submitted Memo"
    APPROVE_MEMO = "approve_memo", "Approved Memo"
    REJECT_MEMO = "reject_memo", "Rejected Memo"
    CANCEL_MEMO = "cancel_memo", "Cancelled Memo"
    VIEW_MEMO = "view_memo", "Viewed Memo"

    # Blog
    ADD_NEW_BLOG = "add_new_blog", "Added New Blog"
    EDIT_BLOG = "edit_blog", "Edited Blog"
    SAVE_AS_DRAFT = "save_as_draft", "Saved Blog as Draft"
    DELETE_BLOG = "delete_blog", "Deleted Blog"
    PERMANENTLY_DELETE_BLOG = "permanently_delete_blog", "Permanently Deleted Blog"
    RESTORE_BLOG = "restore_blog", "Restored Blog"

    

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
