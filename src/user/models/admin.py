from enum import Enum

from django.db import models


class PermissionModule(Enum):
    SIDEBAR = "SIDEBAR"
    OVERVIEW = "OVERVIEW"
    USER = "USER"
    SETTINGS = "SETTINGS"
    CORRESPONDENCE = "CORRESPONDENCE"
    MEMO = "MEMO"
    LEAVE = "LEAVE"
    RECRUITMENT = "RECRUITMENT"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace("_", " ").title()) for item in cls]

    @classmethod
    def values(cls):
        return [item.value for item in cls]


class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=50, choices=PermissionModule.choices())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["module", "name"]


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, related_name="roles")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
