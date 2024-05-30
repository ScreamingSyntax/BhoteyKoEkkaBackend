from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

class UserManager(BaseUserManager):
    def create_user(self, user_name, password=None, **extra_fields):
        if not user_name:
            raise ValueError(_('The user_name field must be set'))
        user_name = self.normalize_email(user_name)  # Use normalize_email for email fields
        user = self.model(user_name=user_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(user_name, password, **extra_fields)

class BaseUser(AbstractBaseUser, PermissionsMixin):
    user_name = models.CharField(max_length=10, unique=True)
    USER_TYPES = (
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('cook', 'Cook'),
        ('cashier', 'Cashier'),

    )
    USERNAME_FIELD = 'user_name'
    password = models.TextField()
    role = models.CharField(max_length=20, choices=USER_TYPES)
    objects = UserManager()
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.user_name  
