import logging
import uuid
from decimal import Decimal, InvalidOperation
from typing import Optional

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


logger = logging.getLogger(__name__)


class Manager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        return self._create_user(email, password, **extra_fields)


class Department(models.Model):
    """Department/Unit for staff organization."""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('director', 'Director'),
        ('hr_manager', 'HR Manager'),
        ('general_staff', 'General Staff'),
    ]
    
    LOCATION_CHOICES = [
        ('headquarters', 'Headquarters'),
        ('branch_office', 'Branch Office'),
        ('regional_office', 'Regional Office'),
        ('remote', 'Remote'),
    ]

    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=50, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='general_staff')
    
    # Staff Profile Fields
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    position = models.CharField(max_length=255, blank=True, null=True, help_text="Job title/position")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='headquarters')
    date_joined_org = models.DateField(null=True, blank=True, help_text="Date joined organization")
    profile_photo = models.ImageField(upload_to='profiles/%Y/%m/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True, help_text="Short bio/description")
    
    # Contact Info
    office_phone = models.CharField(max_length=50, blank=True, null=True)
    office_extension = models.CharField(max_length=10, blank=True, null=True)
    
    # Reporting Structure
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )
    
    # Performance fields
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    performance_points = models.IntegerField(default=0)
    
    # Legacy fields
    is_verified = models.BooleanField(default=True)
    is_buyer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_merchant = models.BooleanField(default=False)
    admin_invite_accepted = models.BooleanField(default=False)
    admin_invite_sent = models.BooleanField(default=False)
    ibank_onboarded = models.BooleanField(default=False)
    kyc_completed = models.BooleanField(default=False)
    send_email_notifications = models.BooleanField(default=True)
    send_app_notifications = models.BooleanField(default=True)
    send_sms_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = Manager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.phone == "":
            self.phone = None
        super().save(*args, **kwargs)

    @property
    def is_super_admin(self):
        return self.role == 'super_admin'

    @property
    def is_director(self):
        return self.role == 'director'

    @property
    def is_hr_manager(self):
        return self.role == 'hr_manager'

    @property
    def is_general_staff(self):
        return self.role == 'general_staff'    @property
    def role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'Unknown')

    @property
    def initials(self):
        if self.name:
            parts = self.name.split()
            return ''.join([p[0].upper() for p in parts[:2]])
        return self.email[0].upper() if self.email else 'U'

    @property
    def full_position(self):
        """Return position with department context."""
        if self.position and self.department:
            return f"{self.position}, {self.department.name}"
        return self.position or self.role_display

    def generate_employee_id(self):
        """Generate unique employee ID."""
        if not self.employee_id:
            prefix = "KMD"
            import random
            self.employee_id = f"{prefix}-{random.randint(1000, 9999)}"
        return self.employee_id


class StaffActivity(models.Model):
    """Track daily staff activities for heatmap visualization."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    date = models.DateField()
    activity_count = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    approvals_given = models.IntegerField(default=0)
    correspondence_handled = models.IntegerField(default=0)
    memos_processed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = 'Staff Activity'
        verbose_name_plural = 'Staff Activities'

    def __str__(self):
        return f"{self.user.name} - {self.date}"

    @property
    def activity_level(self):
        """Return activity level for heatmap (0-4)."""
        if self.activity_count == 0:
            return 0
        elif self.activity_count <= 3:
            return 1
        elif self.activity_count <= 6:
            return 2
        elif self.activity_count <= 10:
            return 3
        return 4


class PerformanceRecord(models.Model):
    """Monthly performance records for staff."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='performance_records'
    )
    month = models.DateField(help_text="First day of the month")
    
    # Performance Metrics
    tasks_assigned = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    tasks_on_time = models.IntegerField(default=0)
    
    approvals_pending = models.IntegerField(default=0)
    approvals_given = models.IntegerField(default=0)
    avg_approval_time_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    correspondence_sent = models.IntegerField(default=0)
    correspondence_received = models.IntegerField(default=0)
    avg_response_time_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Calculated scores
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    points_earned = models.IntegerField(default=0)
    
    # Ranking
    department_rank = models.IntegerField(null=True, blank=True)
    overall_rank = models.IntegerField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'month']
        ordering = ['-month']
        verbose_name = 'Performance Record'
        verbose_name_plural = 'Performance Records'

    def __str__(self):
        return f"{self.user.name} - {self.month.strftime('%B %Y')}"

    @property
    def completion_rate(self):
        if self.tasks_assigned > 0:
            return round((self.tasks_completed / self.tasks_assigned) * 100, 1)
        return 0

    @property
    def on_time_rate(self):
        if self.tasks_completed > 0:
            return round((self.tasks_on_time / self.tasks_completed) * 100, 1)
        return 0


class StaffTask(models.Model):
    """Tasks assigned to staff members."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='staff_assigned_tasks'
    )
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='staff_tasks_assigned'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Related items
    related_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 'memo', 'correspondence', 'approval'")
    related_id = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'due_date', '-created_at']

    def __str__(self):
        return self.title[:50]

    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return self.due_date < timezone.now().date()
        return False

    @property
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None
