# filepath: c:\Users\Administrator\donchess\KMDMC_ERP\src\correspondence\management\commands\seed_correspondence_data.py
"""
Management command to seed correspondence sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from correspondence.models import (
    Organization, Category, Classification, Correspondence,
    CorrespondenceActivity, CorrespondenceComment, CorrespondenceTemplate
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed correspondence module with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing correspondence data...')
            Correspondence.objects.all().delete()
            Organization.objects.all().delete()
            Category.objects.all().delete()
            Classification.objects.all().delete()
            CorrespondenceTemplate.objects.all().delete()

        self.stdout.write('Seeding correspondence data...')
        
        self.create_organizations()
        self.create_categories()
        self.create_classifications()
        self.create_templates()
        self.create_correspondences()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded correspondence data!'))

    def create_organizations(self):
        organizations = [
            {
                'name': 'Ministry of Health',
                'short_name': 'MOH',
                'organization_type': 'Government',
                'email': 'info@moh.go.tz',
                'phone': '+255 22 212 1234',
                'contact_person': 'Dr. James Mwangi',
            },
            {
                'name': 'Tanzania Revenue Authority',
                'short_name': 'TRA',
                'organization_type': 'Government',
                'email': 'info@tra.go.tz',
                'phone': '+255 22 211 9999',
                'contact_person': 'Ms. Sarah Kimaro',
            },
            {
                'name': 'National Health Insurance Fund',
                'short_name': 'NHIF',
                'organization_type': 'Government',
                'email': 'info@nhif.or.tz',
                'phone': '+255 22 213 5678',
                'contact_person': 'Mr. John Massawe',
            },
            {
                'name': 'World Health Organization',
                'short_name': 'WHO',
                'organization_type': 'International',
                'email': 'whotz@who.int',
                'phone': '+255 22 211 1234',
                'contact_person': 'Dr. Maria Santos',
            },
            {
                'name': 'USAID Tanzania',
                'short_name': 'USAID',
                'organization_type': 'International',
                'email': 'tanzania@usaid.gov',
                'phone': '+255 22 229 4000',
                'contact_person': 'Mr. Robert Brown',
            },
            {
                'name': 'Muhimbili National Hospital',
                'short_name': 'MNH',
                'organization_type': 'Hospital',
                'email': 'info@mnh.or.tz',
                'phone': '+255 22 215 0096',
                'contact_person': 'Dr. Grace Mbwambo',
            },
            {
                'name': 'Tanzania Medical Association',
                'short_name': 'TMA',
                'organization_type': 'Association',
                'email': 'info@tma.or.tz',
                'phone': '+255 22 211 7456',
                'contact_person': 'Dr. Peter Mtui',
            },
            {
                'name': 'Medical Stores Department',
                'short_name': 'MSD',
                'organization_type': 'Government',
                'email': 'info@msd.go.tz',
                'phone': '+255 22 286 0890',
                'contact_person': 'Mr. Emmanuel Mwakyusa',
            },
        ]
        
        for org_data in organizations:
            Organization.objects.get_or_create(
                name=org_data['name'],
                defaults=org_data
            )
        
        self.stdout.write(f'  Created {len(organizations)} organizations')

    def create_categories(self):
        categories = [
            {'name': 'General Inquiry', 'code': 'GEN', 'color': 'blue'},
            {'name': 'Funding Request', 'code': 'FUND', 'color': 'green'},
            {'name': 'Partnership', 'code': 'PART', 'color': 'purple'},
            {'name': 'Complaint', 'code': 'COMP', 'color': 'red'},
            {'name': 'Report Submission', 'code': 'RPT', 'color': 'orange'},
            {'name': 'Policy Matter', 'code': 'POL', 'color': 'teal'},
            {'name': 'Legal Matter', 'code': 'LEGAL', 'color': 'gray'},
            {'name': 'Human Resources', 'code': 'HR', 'color': 'pink'},
            {'name': 'Procurement', 'code': 'PROC', 'color': 'indigo'},
            {'name': 'Technical Request', 'code': 'TECH', 'color': 'cyan'},
        ]
        
        for cat_data in categories:
            Category.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
        
        self.stdout.write(f'  Created {len(categories)} categories')

    def create_classifications(self):
        classifications = [
            {'name': 'Public', 'level': 'public', 'color': 'green', 'requires_approval': False},
            {'name': 'Internal Use Only', 'level': 'internal', 'color': 'blue', 'requires_approval': False},
            {'name': 'Confidential', 'level': 'confidential', 'color': 'orange', 'requires_approval': True},
            {'name': 'Secret', 'level': 'secret', 'color': 'red', 'requires_approval': True},
        ]
        
        for class_data in classifications:
            Classification.objects.get_or_create(
                level=class_data['level'],
                defaults=class_data
            )
        
        self.stdout.write(f'  Created {len(classifications)} classifications')

    def create_templates(self):
        user = User.objects.first()
        
        templates = [
            {
                'name': 'Standard Acknowledgement',
                'description': 'Template for acknowledging receipt of correspondence',
                'subject_template': 'RE: {{original_subject}} - Acknowledgement',
                'body_template': '''Dear {{recipient_name}},

We acknowledge receipt of your correspondence dated {{date_received}} regarding {{subject}}.

Your reference number is {{reference_number}}.

We will review your matter and respond accordingly within {{response_days}} working days.

Best regards,
{{sender_name}}
{{sender_title}}
KMDMC'''
            },
            {
                'name': 'Request for Information',
                'description': 'Template for requesting additional information',
                'subject_template': 'Request for Additional Information - {{reference_number}}',
                'body_template': '''Dear {{recipient_name}},

Reference is made to your correspondence dated {{date_received}} with reference {{external_reference}}.

In order to process your request, we kindly require the following additional information:

{{required_information}}

Please submit the requested information within {{deadline_days}} working days.

Best regards,
{{sender_name}}
{{sender_title}}
KMDMC'''
            },
            {
                'name': 'Standard Response',
                'description': 'General response template',
                'subject_template': 'RE: {{original_subject}}',
                'body_template': '''Dear {{recipient_name}},

Reference is made to your correspondence dated {{date_received}} regarding {{subject}}.

{{response_body}}

Should you have any further queries, please do not hesitate to contact us.

Best regards,
{{sender_name}}
{{sender_title}}
KMDMC'''
            },
        ]
        
        for tmpl_data in templates:
            CorrespondenceTemplate.objects.get_or_create(
                name=tmpl_data['name'],
                defaults={**tmpl_data, 'created_by': user}
            )
        
        self.stdout.write(f'  Created {len(templates)} templates')

    def create_correspondences(self):
        organizations = list(Organization.objects.all())
        categories = list(Category.objects.all())
        classifications = list(Classification.objects.all())
        users = list(User.objects.filter(is_active=True))
        
        if not users:
            self.stdout.write(self.style.WARNING('  No users found. Skipping correspondence creation.'))
            return
        
        subjects = [
            'Request for Budget Approval - Q1 2026',
            'Annual Report Submission 2025',
            'Partnership Proposal for Community Health Program',
            'Inquiry about Medical Equipment Procurement',
            'Staff Training Program Request',
            'Monthly Performance Report',
            'Complaint Regarding Service Delivery',
            'Request for Meeting - Policy Discussion',
            'Funding Application - HIV/AIDS Prevention Program',
            'Technical Assistance Request',
            'Audit Report Review Request',
            'License Renewal Application',
            'Research Collaboration Proposal',
            'Emergency Supply Request',
            'Quality Improvement Initiative',
        ]
        
        statuses = ['new', 'pending_action', 'in_progress', 'assigned', 'replied', 'archived']
        priorities = ['low', 'normal', 'normal', 'normal', 'high', 'urgent']
        
        created_count = 0
        for i in range(20):
            subject = random.choice(subjects)
            org = random.choice(organizations)
            cat = random.choice(categories) if categories else None
            classification = random.choice(classifications) if classifications else None
            logged_by = random.choice(users)
            assigned_to = random.choice(users) if random.random() > 0.3 else None
            
            days_ago = random.randint(1, 60)
            date_received = timezone.now() - timedelta(days=days_ago)
            due_date = (timezone.now() + timedelta(days=random.randint(1, 30))).date()
            
            corr_type = random.choice(['incoming', 'incoming', 'incoming', 'outgoing'])
            status = random.choice(statuses)
            priority = random.choice(priorities)
            
            corr = Correspondence.objects.create(
                subject=f"{subject} - {org.short_name or org.name[:3]}",
                correspondence_type=corr_type,
                organization=org,
                contact_name=org.contact_person,
                category=cat,
                classification=classification,
                status=status,
                priority=priority,
                is_confidential=random.random() > 0.8,
                requires_action=random.random() > 0.5,
                date_received=date_received if corr_type == 'incoming' else None,
                date_sent=date_received if corr_type == 'outgoing' else None,
                due_date=due_date if random.random() > 0.3 else None,
                summary=f"This correspondence is regarding {subject.lower()}. Additional details pending review.",
                logged_by=logged_by,
                assigned_to=assigned_to,
                assigned_by=logged_by if assigned_to else None,
                assigned_at=timezone.now() if assigned_to else None,
            )
            
            # Create activity log
            CorrespondenceActivity.objects.create(
                correspondence=corr,
                action='received' if corr_type == 'incoming' else 'created',
                description=f"Correspondence {corr.reference_number} was logged",
                performed_by=logged_by,
                is_automated=True
            )
            
            # Add random comments
            if random.random() > 0.5:
                CorrespondenceComment.objects.create(
                    correspondence=corr,
                    content="Please review and advise on the appropriate action.",
                    is_internal=True,
                    author=logged_by
                )
            
            created_count += 1
        
        self.stdout.write(f'  Created {created_count} correspondence items')
