from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from PIL import Image


# Create your models here.


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=True,
            last_login=now,
            date_joined=now,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def tokens(self):
        return ""


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile",
    )
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="profiles", blank=True, null=True)
    bio = models.TextField(null=True, blank=True)


class Contributor(models.Model):
    user = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="contributions",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="contributors",
        unique=False,
    )
    accepted = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True
    )
    date_accepted = models.DateTimeField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    def get_profile(self):
        return self.user.profile

    def save(self, *args, **kwargs):
        if self.user == self.project.user:
            return ValidationError(
                "You are the manager and cannot be a contributor to this project"
            )
        super(Contributor, self).save(*args, **kwargs)


@receiver(models.signals.post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(models.signals.post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)