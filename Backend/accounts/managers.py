from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

PHONE_REGEX = r"(^923[0-9]{9}$)"

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password, **extra_fields):
        """
        Create and save a User with the given phone and password.
        """
        if not phone:
            raise ValidationError(_('Phone number must be set'))
        if self.validate_phone(phone):
            user = self.model(phone=phone, **extra_fields)
            user.set_password(password)
            user.save()
            return user
        else:
            raise ValidationError(_('Incorrect phone number format'))

    def create_superuser(self, phone, password, **extra_fields):
        """
        Create and save a SuperUser with the given phone and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValidationError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValidationError(_('Superuser must have is_superuser=True.'))
        if self.validate_phone(phone):
            return self.create_user(phone, password, **extra_fields)
        else:
            raise ValidationError(_('Phone number must be in the format 923xxxxxxxxx'))

    def validate_phone(self, phone):
        if len(phone) == 12 and re.match(PHONE_REGEX, phone):
            return True
        return False
