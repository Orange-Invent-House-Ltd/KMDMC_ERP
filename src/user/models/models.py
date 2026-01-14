import logging
import uuid
from decimal import Decimal, InvalidOperation
from typing import Optional

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from user.models.admin import Role


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
        extra_fields.setdefault("is_active", False)

        return self._create_user(email, password, **extra_fields)


class Department(models.Model):
    """Department/Unit for staff organization."""
    name = models.CharField(max_length=255)
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
    LOCATION_CHOICES = [
        ('headquarters', 'Headquarters'),
        ('branch_office', 'Branch Office'),
        ('regional_office', 'Regional Office'),
        ('remote', 'Remote'),
    ]

    username = models.CharField(max_length=150, unique=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=50, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    
    # Staff Profile Fields
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='headquarters')
    date_joined_org = models.DateField(null=True, blank=True, help_text="Date joined organization")
    profile_photo = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True, help_text="Short bio/description")
    office_phone = models.CharField(max_length=50, blank=True, null=True)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    performance_points = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
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
    def initials(self):
        if self.name:
            parts = self.name.split()
            return ''.join([p[0].upper() for p in parts[:2]])
        return self.email[0].upper() if self.email else 'U'

    @property
    def full_position(self):
        """Return position with department context."""
        if self.role and self.department:
            return f"{self.role.name}, {self.department.name}"
        return self.role_display

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


