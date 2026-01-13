from django.db import models
from django.conf import settings
from django.utils import timezone


class Correspondence(models.Model):
    """Main correspondence model for incoming/outgoing mail."""
    TYPE_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'External'),
    ]

    STATUS_CHOICES = [
        ('pending_action', 'Pending_Needs_Approval'),
        ('new', 'New'),
        ("read", "Read"),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
        ('closed', 'Closed'),
    ]

    CATEGORY_CHOICES = [
        ('finance', 'Finance'),
        ('HR', 'Human Resources'),
        ('project', 'Project'),
        ('logistics', 'Logistics')
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_correspondences'
    )

    through = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='copied_correspondences'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_correspondences'
    )

    reference_number = models.CharField(max_length=100, unique=True)
    external_sender = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    requires_action = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)
    md_note = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    daily_serial = models.PositiveIntegerField(null=True, blank=True)
    serial_date = models.DateField(null=True, blank=True)
    is_confidential = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='internal')
    image = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference_number} - {self.subject[:50]}"
    
    def save(self, *args, **kwargs):
        today = timezone.now().date()
        if not self.reference_number:
            last = (
                Correspondence.objects
                .filter(serial_date=today)
                .aggregate(models.Max("daily_serial"))
                .get("daily_serial__max") or 0
            )

            self.daily_serial = last + 1
            self.serial_date = today

            date_str = today.strftime("%d/%m")
            self.reference_number = f"KDN-{date_str}/{self.daily_serial}"

        super().save(*args, **kwargs)