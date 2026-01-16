from dataclasses import dataclass

from user.models.admin import PermissionModule


@dataclass
class PERMISSIONS:
    """
    Central permission registry for the ERP system.
    """

    # SUPER_ADMIN PERMISSIONS
    CAN_VIEW_PERMISSIONS = "CAN_VIEW_PERMISSIONS"
    CAN_ADD_PERMISSIONS_TO_ROLE = "CAN_ADD_PERMISSIONS_TO_ROLE"
    CAN_UPDATE_PERMISSIONS = "CAN_UPDATE_PERMISSIONS"
    CAN_DELETE_PERMISSIONS = "CAN_DELETE_PERMISSIONS"
    CAN_ADD_ROLES = "CAN_ADD_ROLES"
    CAN_UPDATE_ROLES = "CAN_UPDATE_ROLES"
    CAN_DELETE_ROLES = "CAN_DELETE_ROLES"
    CAN_VIEW_ROLES = "CAN_VIEW_ROLES"

    # MD ROLES
    CAN_ARCHIVE_CORRESPONDENCE = "CAN_ARCHIVE_CORRESPONDENCE"
    CAN_GIVE_FINAL_APPROVAL = "CAN_GIVE_FINAL_APPROVAL"
    CAN_DELETE_DEPARTMENT = "CAN_DELETE_DEPARTMENT"
    CAN_DELEGATE_AUTHORITY = "CAN_DELEGATE_AUTHORITY"

    # CORRESPONDENCE
    CAN_VIEW_CORRESPONDENCE = "CAN_VIEW_CORRESPONDENCE"
    CAN_CREATE_CORRESPONDENCE = "CAN_CREATE_CORRESPONDENCE"
    CAN_UPDATE_CORRESPONDENCE = "CAN_UPDATE_CORRESPONDENCE"
    

    #===== HR=======
    # DEPARTMENT / REGISTRY
    CAN_VIEW_DEPARTMENTS = "CAN_VIEW_DEPARTMENTS"
    CAN_ADD_DEPARTMENT = "CAN_ADD_DEPARTMENT"
    CAN_UPDATE_DEPARTMENT = "CAN_UPDATE_DEPARTMENT"
    

    # STAFF
    CAN_ADD_STAFF = "CAN_ADD_STAFF"
    CAN_UPDATE_STAFF = "CAN_UPDATE_STAFF"
    CAN_VIEW_STAFF_DETAILS = "CAN_VIEW_STAFF_DETAILS"

    # ======HR========


    # TASK MANAGEMENT
    CAN_ASSIGN_TASKS = "CAN_ASSIGN_TASKS"
    CAN_EXECUTE_TASKS = "CAN_EXECUTE_TASKS"
    CAN_VIEW_TASKS = "CAN_VIEW_TASKS"


    # SYSTEM / IT
    CAN_ACCESS_SYSTEM_ADMIN = "CAN_ACCESS_SYSTEM_ADMIN"



SYSTEM_PERMISSIONS = {
    # SUPER_ADMIN PERMISSIONS
    PERMISSIONS.CAN_VIEW_PERMISSIONS: {
        "description": "Can view all permissions in the system",
        "module": PermissionModule.OVERVIEW.value,
    },
    PERMISSIONS.CAN_ACCESS_SYSTEM_ADMIN: {
        "description": "Can access system admin and technical settings",
        "module": PermissionModule.OVERVIEW.value,
    },
    PERMISSIONS.CAN_ADD_PERMISSIONS_TO_ROLE: {
        "description": "Can add permissions to roles",
        "module": PermissionModule.OVERVIEW.value,
    },
    PERMISSIONS.CAN_UPDATE_PERMISSIONS: {
        "description": "Can update existing permissions",
        "module": PermissionModule.OVERVIEW.value,
    },
    PERMISSIONS.CAN_DELETE_PERMISSIONS: {
        "description": "Can delete permissions from the system",
        "module": PermissionModule.OVERVIEW.value,
    },
    PERMISSIONS.CAN_ADD_ROLES: {
        "description": "Can create new roles",
        "module": PermissionModule.OVERVIEW.value,
    },
    PERMISSIONS.CAN_UPDATE_ROLES: {
        "description": "Can update existing roles",
        "module": PermissionModule.OVERVIEW.value,
    },
    PERMISSIONS.CAN_DELETE_ROLES: {
        "description": "Can delete roles from the system",
        "module": PermissionModule.OVERVIEW.value,
    },

    PERMISSIONS.CAN_VIEW_ROLES: {
        "description": "Can view all roles in the system",
        "module": PermissionModule.OVERVIEW.value,
    },

    
    # CORRESPONDENCE
    PERMISSIONS.CAN_VIEW_CORRESPONDENCE: {
        "description": "Can view internal and external correspondence",
        "module": PermissionModule.CORRESPONDENCE.value,
    },

    PERMISSIONS.CAN_CREATE_CORRESPONDENCE: {
        "description": "Can create and submit internal correspondence",
        "module": PermissionModule.CORRESPONDENCE.value,
    },

    PERMISSIONS.CAN_UPDATE_CORRESPONDENCE: {
        "description": "Can update and edit correspondence drafts",
        "module": PermissionModule.CORRESPONDENCE.value,
    },

    # MD ROLES
    PERMISSIONS.CAN_ARCHIVE_CORRESPONDENCE: {
        "description": "Can archive correspondence",
        "module": PermissionModule.EXECUTIVE.value,
    },

    PERMISSIONS.CAN_GIVE_FINAL_APPROVAL: {
        "description": "Can give final approval and issue directives",
        "module": PermissionModule.EXECUTIVE.value,
    },

        PERMISSIONS.CAN_DELETE_DEPARTMENT: {
        "description": "Can delete existing departments",
        "module": PermissionModule.EXECUTIVE.value,
    },
    PERMISSIONS.CAN_DELEGATE_AUTHORITY: {
        "description": "Can delegate authority on a time-bound basis",
        "module": PermissionModule.EXECUTIVE.value,
    },

    # TASK MANAGEMENT
    PERMISSIONS.CAN_ASSIGN_TASKS: {
        "description": "Can assign tasks to staff",
        "module": PermissionModule.TASKS.value,
    },

    PERMISSIONS.CAN_EXECUTE_TASKS: {
        "description": "Can execute assigned tasks",
        "module": PermissionModule.TASKS.value,
    },

    # STAFF / HR
    PERMISSIONS.CAN_VIEW_STAFF_DETAILS: {
        "description": "Can view staff personnel files",
        "module": PermissionModule.HR.value,
    },

    PERMISSIONS.CAN_ADD_STAFF: {
        "description": "Can add new staff members",
        "module": PermissionModule.HR.value,
    },

    PERMISSIONS.CAN_UPDATE_STAFF: {
        "description": "Can update existing staff information",
        "module": PermissionModule.HR.value,
    },

    PERMISSIONS.CAN_ADD_DEPARTMENT: {
        "description": "Can add new departments",
        "module": PermissionModule.HR.value,
    },

    PERMISSIONS.CAN_VIEW_DEPARTMENTS: {
        "description": "Can view all departments",
        "module": PermissionModule.HR.value,
    },

    PERMISSIONS.CAN_UPDATE_DEPARTMENT: {
        "description": "Can update existing department details",
        "module": PermissionModule.HR.value,
    },

}
 