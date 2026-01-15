from django.core.management.base import BaseCommand
from user.models.admin import Permission, Role, PermissionModule

class Command(BaseCommand):
    help = "Seed initial roles and permissions"

    def handle(self, *args, **options):
        # Seed permissions
        permissions = []
        for module_value, module_label in PermissionModule.choices():
            perm, created = Permission.objects.get_or_create(
                name=f"{module_label} Access",
                module=module_value,
                defaults={
                    "description": f"Access to {module_label} features"
                }
            )
            permissions.append(perm)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created permission: {perm.name}"))
            else:
                self.stdout.write(f"Permission already exists: {perm.name}")

        # Seed roles
        admin_role, _ = Role.objects.get_or_create(
            name="Admin",
            code="ADMIN",
            defaults={
                "description": "Administrator with all permissions"
            }
        )
        admin_role.permissions.set(permissions)
        admin_role.save()
        self.stdout.write(self.style.SUCCESS("Admin role seeded."))

        user_role, _ = Role.objects.get_or_create(
            name="User",
            code="USER",
            defaults={
                "description": "Standard user with limited permissions"
            }
        )
        # Example: assign only SIDEBAR and OVERVIEW permissions
        user_perms = [p for p in permissions if p.module in [PermissionModule.SIDEBAR.value, PermissionModule.OVERVIEW.value]]
        user_role.permissions.set(user_perms)
        user_role.save()
        self.stdout.write(self.style.SUCCESS("User role seeded."))

        self.stdout.write(self.style.SUCCESS("Roles and permissions seeding complete."))
