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
        ('draft', 'Draft'),
        ("read", "Read"),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
        ('closed', 'Closed'),
        ('replied', 'Replied'),
        ('forwarded', 'Forwarded'),
    ]

    CATEGORY_CHOICES = [
        ('finance', 'Finance'),
        ('HR', 'Human Resources'),
        ('project', 'Project'),
        ('logistics', 'Logistics')
    ]
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )

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
    delegated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='correspondences_delegate'
    )

    reference_number = models.CharField(max_length=100, unique=True)
    external_sender = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
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
    image_urls = models.JSONField(null=True, blank=True)
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

class CorrespondenceDelegate(models.Model):
    correspondence = models.ForeignKey(Correspondence, on_delete=models.CASCADE, related_name='delegates')
    delegated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delegated_correspondences')
    delegated_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_delegated_correspondences')
    note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    delegated_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Delegate for {self.correspondence.subject} - {self.delegated_to.username}"
    