from django.db import models
from users.models import User
from PIL import Image
from django.utils import timezone

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
