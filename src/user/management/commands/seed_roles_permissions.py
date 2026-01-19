from django.core.management.base import BaseCommand
from django.db import transaction

from user.models.admin import Permission, Role
from utils.permissions import PERMISSIONS, SYSTEM_PERMISSIONS


ROLE_PERMISSION_MAP = {
    "SUPER_ADMIN": {
        "name": "Super Admin",
        "description": "Full system control",
        "permissions": list(SYSTEM_PERMISSIONS.keys()),
    },

    "MANAGING_DIRECTOR": {
        "name": "Managing Director",
        "description": "Executive authority",
        "permissions": [
            PERMISSIONS.CAN_VIEW_CORRESPONDENCE,
            PERMISSIONS.CAN_CREATE_CORRESPONDENCE,
            PERMISSIONS.CAN_UPDATE_CORRESPONDENCE,
            PERMISSIONS.CAN_ARCHIVE_CORRESPONDENCE,
            PERMISSIONS.CAN_GIVE_FINAL_APPROVAL,
            PERMISSIONS.CAN_CREATE_DEPARTMENT,
            PERMISSIONS.CAN_UPDATE_DEPARTMENT,
            PERMISSIONS.CAN_VIEW_DEPARTMENTS,
            PERMISSIONS.CAN_DELETE_DEPARTMENT,
            PERMISSIONS.CAN_DELEGATE_AUTHORITY,
            PERMISSIONS.CAN_VIEW_DASHBOARD,
            PERMISSIONS.CAN_ASSIGN_TASKS,
            PERMISSIONS.CAN_VIEW_TASKS,
            PERMISSIONS.CAN_VIEW_STAFF_DETAILS,
            PERMISSIONS.CAN_ADD_ROLES,
            PERMISSIONS.CAN_UPDATE_ROLES,
            PERMISSIONS.CAN_DELETE_ROLES,
            PERMISSIONS.CAN_VIEW_PERFORMANCE_OVERVIEW,
            PERMISSIONS.CAN_ACCESS_SYSTEM_ADMIN,

        ],
    },

    "GENERAL_MANAGER": {
        "name": "General Manager",
        "description": "Department-level management",
        "permissions": [
            PERMISSIONS.CAN_VIEW_CORRESPONDENCE,
            PERMISSIONS.CAN_CREATE_CORRESPONDENCE,
            PERMISSIONS.CAN_UPDATE_CORRESPONDENCE,
            PERMISSIONS.CAN_ASSIGN_TASKS,
            PERMISSIONS.CAN_VIEW_TASKS,
            PERMISSIONS.CAN_VIEW_DEPARTMENTS,
            PERMISSIONS.CAN_VIEW_STAFF_DETAILS,
        ],
    },

    "SUPERVISOR": {
        "name": "Supervisor",
        "description": "Unit-level supervision",
        "permissions": [
            PERMISSIONS.CAN_VIEW_CORRESPONDENCE,
            PERMISSIONS.CAN_CREATE_CORRESPONDENCE,
            PERMISSIONS.CAN_ASSIGN_TASKS,
            PERMISSIONS.CAN_VIEW_TASKS,
            PERMISSIONS.CAN_VIEW_STAFF_DETAILS,
        ],
    },

    "HR": {
        "name": "HR",
        "description": "Human Resources",
        "permissions": [
            PERMISSIONS.CAN_VIEW_DEPARTMENTS,
            PERMISSIONS.CAN_ADD_DEPARTMENT,
            PERMISSIONS.CAN_UPDATE_DEPARTMENT,
            PERMISSIONS.CAN_VIEW_STAFF_DETAILS,
            PERMISSIONS.CAN_ADD_STAFF,
            PERMISSIONS.CAN_UPDATE_STAFF,
            PERMISSIONS.CAN_CREATE_APPRAISAL_TEMPLATE
        ],
    },

    "STAFF": {
        "name": "Staff",
        "description": "Operational staff",
        "permissions": [
            PERMISSIONS.CAN_VIEW_CORRESPONDENCE,
            PERMISSIONS.CAN_VIEW_TASKS,
            PERMISSIONS.CAN_EXECUTE_TASKS,
        ],
    },
}


class Command(BaseCommand):
    help = "Seeds, updates, and cleans up ERP permissions and roles"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Starting permission sync..."))
        self.stdout.write(f"Found {len(SYSTEM_PERMISSIONS)} permissions")

        created_count = 0
        updated_count = 0
        deleted_count = 0

        with transaction.atomic():

            # ----------------------------
            # Sync Permissions
            # ----------------------------
            for name, data in SYSTEM_PERMISSIONS.items():
                _, created = Permission.objects.update_or_create(
                    name=name,
                    defaults={
                        "description": data["description"],
                        "module": data["module"],
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            # ----------------------------
            # Delete Removed Permissions
            # ----------------------------
            removed_permissions = Permission.objects.exclude(
                name__in=SYSTEM_PERMISSIONS.keys()
            )

            deleted_count = removed_permissions.count()
            removed_permissions.delete()

            # ----------------------------
            # Sync Roles
            # ----------------------------
            self.stdout.write(self.style.MIGRATE_HEADING("Seeding roles..."))

            for code, role_data in ROLE_PERMISSION_MAP.items():
                role, _ = Role.objects.get_or_create(
                    code=code,
                    defaults={
                        "name": role_data["name"],
                        "description": role_data["description"],
                    },
                )

                perms = Permission.objects.filter(name__in=role_data["permissions"])
                role.permissions.set(perms)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ {role.name} → {perms.count()} permissions"
                    )
                )

        # ----------------------------
        # Summary
        # ----------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Sync complete"))
        self.stdout.write(self.style.SUCCESS(f"Created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Deleted: {deleted_count}"))
