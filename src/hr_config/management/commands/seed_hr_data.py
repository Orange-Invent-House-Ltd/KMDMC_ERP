from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import time

from hr_config.models import (
    LeaveType,
    AttendancePolicy,
    LeaveApprovalWorkflow,
    LeaveApprovalStage,
)
from user.models import Permission
from user.models.admin import PermissionModule


class Command(BaseCommand):
    help = 'Seeds initial HR configuration data'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting HR data seeding...'))

        # Seed Leave Types
        self.seed_leave_types()

        # Seed Attendance Policy
        self.seed_attendance_policy()

        # Seed Leave Approval Workflow
        self.seed_leave_approval_workflow()

        # Seed HR_CONFIG Permissions
        self.seed_permissions()

        self.stdout.write(self.style.SUCCESS('HR data seeding completed successfully!'))

    def seed_leave_types(self):
        """Create default leave types."""
        self.stdout.write('Seeding leave types...')

        leave_types = [
            {
                'leave_type_name': 'Annual Leave',
                'description': 'Yearly paid vacation leave for rest and recreation',
                'allowance_days': 30,
                'accrual_frequency': 'monthly',
                'accrual_rate': 2.5,
                'is_paid': True,
                'requires_documentation': False,
                'is_active': True,
                'color_code': '#4CAF50',
            },
            {
                'leave_type_name': 'Sick Leave',
                'description': 'Leave for medical treatment and recovery',
                'allowance_days': 15,
                'accrual_frequency': 'yearly',
                'accrual_rate': 15,
                'is_paid': True,
                'requires_documentation': True,
                'is_active': True,
                'color_code': '#F44336',
            },
            {
                'leave_type_name': 'Maternity Leave',
                'description': 'Leave for expectant and new mothers',
                'allowance_days': 90,
                'accrual_frequency': 'per_event',
                'accrual_rate': 90,
                'is_paid': True,
                'requires_documentation': True,
                'is_active': True,
                'color_code': '#E91E63',
            },
            {
                'leave_type_name': 'Paternity Leave',
                'description': 'Leave for new fathers',
                'allowance_days': 10,
                'accrual_frequency': 'per_event',
                'accrual_rate': 10,
                'is_paid': True,
                'requires_documentation': True,
                'is_active': True,
                'color_code': '#2196F3',
            },
            {
                'leave_type_name': 'Casual Leave',
                'description': 'Short-term leave for personal matters',
                'allowance_days': 12,
                'accrual_frequency': 'yearly',
                'accrual_rate': 12,
                'is_paid': True,
                'requires_documentation': False,
                'is_active': True,
                'color_code': '#FF9800',
            },
            {
                'leave_type_name': 'Unpaid Leave',
                'description': 'Leave without pay for extended personal matters',
                'allowance_days': 30,
                'accrual_frequency': 'yearly',
                'accrual_rate': 30,
                'is_paid': False,
                'requires_documentation': True,
                'is_active': True,
                'color_code': '#9E9E9E',
            },
        ]

        for leave_type_data in leave_types:
            leave_type, created = LeaveType.objects.get_or_create(
                leave_type_name=leave_type_data['leave_type_name'],
                defaults=leave_type_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created leave type: {leave_type.leave_type_name}'))
            else:
                self.stdout.write(f'  - Leave type already exists: {leave_type.leave_type_name}')

    def seed_attendance_policy(self):
        """Create default attendance policy (singleton)."""
        self.stdout.write('Seeding attendance policy...')

        if AttendancePolicy.objects.exists():
            self.stdout.write('  - Attendance policy already exists')
            return

        policy = AttendancePolicy.objects.create(
            shift_start_time=time(9, 0),  # 9:00 AM
            shift_end_time=time(17, 0),   # 5:00 PM
            late_grace_period_minutes=15,
            enable_overtime=True,
            overtime_threshold_minutes=30,
            working_days_per_week=5,
            working_days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            require_check_in=True,
            require_check_out=True,
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Created default attendance policy'))

    def seed_leave_approval_workflow(self):
        """Create default leave approval workflow with stages."""
        self.stdout.write('Seeding leave approval workflow...')

        workflow, created = LeaveApprovalWorkflow.objects.get_or_create(
            workflow_name='Default Leave Approval',
            defaults={
                'is_active': True,
                'enable_auto_approval': False,
                'auto_approve_threshold_days': 0,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created workflow: {workflow.workflow_name}'))

            # Create stages
            stages = [
                {
                    'stage_order': 1,
                    'stage_name': 'Employee Submits Request',
                    'approver_type': 'initiator',
                    'required_role': None,
                    'is_required': True,
                    'can_skip': False,
                },
                {
                    'stage_order': 2,
                    'stage_name': 'Direct Manager Approval',
                    'approver_type': 'direct_manager',
                    'required_role': None,
                    'is_required': True,
                    'can_skip': False,
                },
                {
                    'stage_order': 3,
                    'stage_name': 'HR Review',
                    'approver_type': 'hr_admin',
                    'required_role': None,
                    'is_required': True,
                    'can_skip': False,
                },
            ]

            for stage_data in stages:
                stage = LeaveApprovalStage.objects.create(
                    workflow=workflow,
                    **stage_data
                )
                self.stdout.write(self.style.SUCCESS(f'    ✓ Created stage {stage.stage_order}: {stage.stage_name}'))
        else:
            self.stdout.write(f'  - Workflow already exists: {workflow.workflow_name}')

    def seed_permissions(self):
        """Create HR_CONFIG permissions."""
        self.stdout.write('Seeding HR_CONFIG permissions...')

        permissions = [
            {
                'name': 'View HR Configuration',
                'description': 'Can view HR configuration settings',
                'module': PermissionModule.HR_CONFIG.value,
            },
            {
                'name': 'Manage Appraisal Templates',
                'description': 'Can create, update, and delete appraisal templates',
                'module': PermissionModule.HR_CONFIG.value,
            },
            {
                'name': 'Manage Leave Types',
                'description': 'Can create, update, and delete leave types',
                'module': PermissionModule.HR_CONFIG.value,
            },
            {
                'name': 'Manage Public Holidays',
                'description': 'Can create, update, and delete public holidays',
                'module': PermissionModule.HR_CONFIG.value,
            },
            {
                'name': 'Manage Attendance Policy',
                'description': 'Can update attendance policy settings',
                'module': PermissionModule.HR_CONFIG.value,
            },
            {
                'name': 'Manage Leave Approval Workflows',
                'description': 'Can create, update, and delete leave approval workflows',
                'module': PermissionModule.HR_CONFIG.value,
            },
        ]

        for perm_data in permissions:
            permission, created = Permission.objects.get_or_create(
                name=perm_data['name'],
                defaults=perm_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created permission: {permission.name}'))
            else:
                self.stdout.write(f'  - Permission already exists: {permission.name}')
