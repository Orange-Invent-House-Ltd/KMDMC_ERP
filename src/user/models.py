import logging
import uuid
from decimal import Decimal, InvalidOperation
from typing import Optional

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction


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


class CustomUser(AbstractUser):
    username = None
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=50, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
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
