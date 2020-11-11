from django.db import models
from users.models import User, Contributor
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils import timezone, timesince
from djmoney.models.fields import MoneyField

# Create your models here.
class Project(models.Model):
    PRIORITY_CHOICES = [("H", "High"), ("M", "Medium"), ("L", "Low")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255, null=False, blank=False)
    is_public = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now())
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=5, choices=PRIORITY_CHOICES, default="M")
    documentation = models.TextField(null=True, blank=True)
    icon = models.ImageField(upload_to="icons", blank=True, null=True)

    def save(self, *args, **kwargs):

        if self.due_date is not None:
            if self.due_date < timezone.now().date():
                raise ValueError("Due date cannot be in the past.")

        super().save(*args, **kwargs)

    def count_contributors(self):
        return self.contributors.count()


class Feature(models.Model):
    PRIORITY_CHOICES = [("H", "High"), ("M", "Medium"), ("L", "Low")]
    contributor = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="features",
    )
    project = models.ForeignKey(
        Project,
        related_name="features",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    documentation = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reviews",
    )
    date_reviewed = models.DateTimeField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    merged = models.BooleanField(default=False)
    date_merged = models.DateTimeField(blank=True, null=True)
    cost = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=5, default="M")
    votes = models.IntegerField(default=0)

    def save(self, *args, **kwargs):

        if self.due_date is not None:
            if self.due_date < timezone.now().date():
                raise ValueError("Due date cannot be in the past.")

        super().save(*args, **kwargs)
