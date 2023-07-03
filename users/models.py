from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# Create your models here.

class CustomUserManager(BaseUserManager):
  def create_user(self, email, password=None, first_name='', last_name=''):
    if not email:
      raise ValueError('User must have an email address')

    user = self.model(
      email=self.normalize_email(email),
      first_name=first_name,
      last_name=last_name
    )
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, password=None):
      """
      Creates and saves a superuser with the given email, name, tc and password.
      """
      user = self.create_user(
          email,
          password=password
      )
      user.is_superuser = True
      user.save(using=self._db)
      return user
  # def _create_user(self, email, password, first_name, last_name, **extra_fields):
  #   if not email:
  #     raise ValueError("Email must be provided!")
  #   if not password:
  #     raise ValueError("Email is not provided!")
    
  #   user = self.model(
  #     email = self.normalize_email(email),
  #     first_name = first_name,
  #     last_name = last_name,
  #     **extra_fields
  #   )

  #   user.set_password(password)
  #   user.save(using=self.db)
  #   return user

  # def create_user(self, email, password, first_name, last_name, **extra_fields):
  #   extra_fields.setdefault('is_staff', True)
  #   extra_fields.setdefault('is_active', True)
  #   extra_fields.setdefault('is_superuser', False)
  #   return self.create_user(email, password, first_name, last_name, password, **extra_fields)
  
  # def create_superuser(self, email, password, first_name, last_name, **extra_fields):
  #   extra_fields.setdefault('is_staff', True)
  #   extra_fields.setdefault('is_active', True)
  #   extra_fields.setdefault('is_superuser', True)
  #   return self.create_user(email, password, first_name, last_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
  email = models.EmailField(verbose_name='Email',
      max_length=255,
      unique=True,)
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)

  is_staff = models.BooleanField(default=True)
  is_active = models.BooleanField(default=True)
  is_superuser = models.BooleanField(default=False)

  objects = CustomUserManager()

  USERNAME_FIELD = 'email'

  def __str__(self):
    return self.email
  

  class meta:
    verbose_name = 'User'
    verbose_name_plural = 'Users'




@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  if created:
    Token.objects.create(user=instance)

# class UserProfile(models.Model):
#   user = models.OneToOneField(User, on_delete=models.CASCADE)
#   phone_number = models.IntegerField('Phone Number', blank=True, default=0)