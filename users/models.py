from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.utils import timezone

# User extension classes built with guidance from Sarthak Kumar: 
# https://medium.com/@ksarthak4ever/django-custom-user-model-allauth-for-oauth-20c84888c318

class AccountManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser):
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
        user.set_password(password)
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

class MyAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    stripe_customer_id = models.CharField(max_length=50, unique=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    package_tier = models.IntegerField(blank=False, default=1)
    package_name = models.CharField(max_length=50, blank=False, default="Free Account")
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    # profile_image = ResizedImageField(size=[500,500], upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)
    job_role = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000, blank=True)
    skills = models.CharField(max_length=1000, null=True, blank=True)
    hide_email = models.BooleanField(default=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email