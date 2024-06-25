from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username= None
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    phone = models.CharField(max_length=12, unique=True, help_text="phone must be in this format : 923xxxxxxxxx")

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.phone