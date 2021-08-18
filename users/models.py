from django.db import models
from django import forms
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    AbstractUser)
from django.utils import timezone
from timezone_field import TimeZoneField
from django_resized import ResizedImageField
from checkout.models import Order
import uuid

# User extension classes built with guidance from Sarthak Kumar: 
# https://medium.com/@ksarthak4ever/django-custom-user-model-allauth-for-oauth-20c84888c318

class AccountManager(BaseUserManager):
    def _create_user(self, email, password_clean, is_staff, is_superuser):
        if not email:
            raise ValueError('Please enter a valid email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff, 
            is_active=True,
            is_superuser=is_superuser, 
            last_login=now,
            date_joined=now
        )
        user.set_password(password_clean)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        if not email:
            raise ValueError('Please enter a valid email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=True, 
            is_active=True,
            is_superuser=True, 
            last_login=now,
            date_joined=now
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user


def get_profile_image_filepath(self, filename):
    return f'profile_imgs/{self.pk}_{self.first_name}_{self.last_name}/profile_img.png'

# Image from Pixabay Image by 
# https://pixabay.com/users/wanderercreative-855399/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=973460">Stephanie Edwards</a> from <a href="https://pixabay.com/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=973460
def get_default_profile_image():
    return 'profile_imgs/default_avatar.png'


class MyAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=60, unique=True)
    stripe_customer_id = models.CharField(max_length=150, unique=True, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=150, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=False, default="")
    last_name = models.CharField(max_length=50, blank=False, default="")
    package_tier = models.IntegerField(blank=False, default=1)
    package_name = models.CharField(max_length=50, blank=False, default="Free Account")
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    timezone = TimeZoneField(choices_display='WITH_GMT_OFFSET', default='Europe/London')
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    profile_completed = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    show_profile = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)
    job_role = models.CharField(max_length=255, blank=True, default="")
    industry = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(max_length=1000, blank=True, default="")
    skills = models.CharField(max_length=1000, blank=True)
    hide_email = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    
    def skills_as_list(self):
        return self.skills.split(',')

    def __str__(self):
        return self.email


class Skills(models.Model):
    skill_name = models.CharField(max_length=50, null=False, blank=False, default="")

    def __str__(self):
        return self.skill_name


class Roles(models.Model):
    role_name = models.CharField(max_length=50, null=False, blank=False, default="")

    def __str__(self):
        return self.role_name