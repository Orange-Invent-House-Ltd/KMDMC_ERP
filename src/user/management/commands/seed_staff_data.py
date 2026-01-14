from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from user.models.models import Department, StaffActivity, PerformanceRecord, StaffTask

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed sample staff profile data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding staff profile data...')
        
        # Create Departments
        departments_data = [
            {'name': 'Office of the Managing Director', 'code': 'MD', 'description': 'Executive leadership'},
            {'name': 'General Manager Office', 'code': 'GM', 'description': 'Operational management'},
            {'name': 'Human Resources & Administration', 'code': 'HR', 'description': 'Personnel management'},
            {'name': 'Finance & Accounting', 'code': 'FIN', 'description': 'Financial management'},
            {'name': 'Information & Communication Technology', 'code': 'ICT', 'description': 'IT services'},
            {'name': 'Procurement & Supplies', 'code': 'PROC', 'description': 'Procurement'},
            {'name': 'Legal & Compliance', 'code': 'LEGAL', 'description': 'Legal affairs'},
            {'name': 'Operations', 'code': 'OPS', 'description': 'Operations'},
            {'name': 'Logistics', 'code': 'LOG', 'description': 'Logistics operations'},
            {'name': 'Internal Audit', 'code': 'AUDIT', 'description': 'Internal audit'},
        ]
        
        departments = {}
        for data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'is_active': True
                }
            )
            departments[data['code']] = dept
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(departments)} departments'))
        
        # Create sample staff - Sarah Jenkins (as shown in UI)
        sarah, created = User.objects.get_or_create(
            email='sarah.jenkins@kmdmc.go.tz',
            defaults={
                'name': 'Sarah Jenkins',
                'position': 'Senior Ops Officer',
                'department': departments.get('LOG'),
                'location': 'headquarters',
                'date_joined_org': timezone.now().date() - timedelta(days=2000),
                'employee_id': 'KMD-8842',
                'role': 'general_staff',
                'is_active': True,
                'performance_score': 85,
                'performance_points': 850,
            }
        )
        if created:
            sarah.set_password('password123')
            sarah.save()
        
        self.stdout.write(self.style.SUCCESS(f'Created Sarah Jenkins profile'))
        
        # Update existing users with staff profile info
        staff_updates = [
            ('admin@kmdmc.go.tz', 'System Administrator', 'ICT'),
            ('md@kmdmc.go.tz', 'Managing Director', 'MD'),
            ('gm@kmdmc.go.tz', 'General Manager', 'GM'),
            ('hr.manager@kmdmc.go.tz', 'HR Manager', 'HR'),
            ('finance.head@kmdmc.go.tz', 'Head of Finance', 'FIN'),
            ('ict.head@kmdmc.go.tz', 'Head of ICT', 'ICT'),
        ]
        
        for email, position, dept_code in staff_updates:
            try:
                user = User.objects.get(email=email)
                user.position = position
                user.department = departments.get(dept_code)
                user.location = 'headquarters'
                if not user.employee_id:
                    user.employee_id = f"KMD-{random.randint(1000, 9999)}"
                if not user.date_joined_org:
                    user.date_joined_org = timezone.now().date() - timedelta(days=random.randint(365, 2000))
                user.performance_score = random.uniform(70, 95)
                user.performance_points = random.randint(600, 950)
                user.save()
            except User.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS('Updated existing staff profiles'))
        
        # Set department heads
        head_map = [
            ('MD', 'md@kmdmc.go.tz'),
            ('GM', 'gm@kmdmc.go.tz'),
            ('HR', 'hr.manager@kmdmc.go.tz'),
            ('FIN', 'finance.head@kmdmc.go.tz'),
            ('ICT', 'ict.head@kmdmc.go.tz'),
            ('LOG', 'sarah.jenkins@kmdmc.go.tz'),
        ]
        
        for dept_code, email in head_map:
            try:
                dept = departments.get(dept_code)
                user = User.objects.get(email=email)
                if dept:
                    dept.head = user
                    dept.save()
            except User.DoesNotExist:
                pass
        
        # Create tasks for Sarah
        gm_user = User.objects.filter(email='gm@kmdmc.go.tz').first()
        
        tasks_data = [
            ('Review Q3 Budget Proposal', 'pending', 'high', 5),
            ('Audit Logistics Inventory', 'in_progress', 'normal', 7),
            ('Approve Vendor Contracts', 'completed', 'normal', -3),
        ]
        
        for title, status, priority, days_offset in tasks_data:
            StaffTask.objects.get_or_create(
                title=title,
                assigned_to=sarah,
                defaults={
                    'status': status,
                    'priority': priority,
                    'due_date': timezone.now().date() + timedelta(days=days_offset),
                    'assigned_by': gm_user,
                    'department': sarah.department,
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created sample tasks'))
        
        # Create activity heatmap data
        today = timezone.now().date()
        for i in range(180):
            date = today - timedelta(days=i)
            if random.random() < 0.3:
                continue
            
            activity_count = random.randint(0, 15)
            StaffActivity.objects.get_or_create(
                user=sarah,
                date=date,
                defaults={
                    'activity_count': activity_count,
                    'tasks_completed': random.randint(0, min(3, activity_count)),
                    'approvals_given': random.randint(0, min(5, activity_count)),
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created activity heatmap data'))
        
        # Create performance records
        for i in range(12):
            month_date = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            PerformanceRecord.objects.get_or_create(
                user=sarah,
                month=month_date,
                defaults={
                    'tasks_assigned': random.randint(15, 30),
                    'tasks_completed': random.randint(12, 28),
                    'tasks_on_time': random.randint(10, 25),
                    'approvals_given': random.randint(100, 150),
                    'avg_response_time_hours': random.uniform(1.0, 4.0),
                    'performance_score': random.uniform(75, 95),
                    'points_earned': random.randint(60, 100),
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created performance records'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Staff Profile Data Seeding Complete!'))
        self.stdout.write(f'  Departments: {Department.objects.count()}')
        self.stdout.write(f'  Staff: {User.objects.filter(is_active=True).count()}')
        self.stdout.write(f'  Tasks: {StaffTask.objects.count()}')
        self.stdout.write(f'  Activity Records: {StaffActivity.objects.count()}')
        self.stdout.write(f'  Performance Records: {PerformanceRecord.objects.count()}')
        self.stdout.write(self.style.SUCCESS('=' * 50))
