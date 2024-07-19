from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('seller', 'Seller'),
    )
    
    username = None
    first_name = models.CharField(
        max_length=255,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z]+$',
            message='First name must contain only letters',
            code='invalid_first_name'
        )]
    )
    last_name = models.CharField(
        max_length=255,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z]+$',
            message='Last name must contain only letters',
            code='invalid_last_name'
        )]
    )
    phone = models.CharField(
        max_length=12,
        unique=True,
        help_text="Phone must be in this format: 923xxxxxxxxx"
    )
    photo = models.ImageField(upload_to='users', blank=True, null=True, default='users/person.png')
    date_of_birth = models.DateField(blank=True, null=True)
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.phone
