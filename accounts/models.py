from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

def generate_activation_token():
    return uuid.uuid4()

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    email_verified = models.BooleanField(default=False)
    activation_token = models.UUIDField(default=generate_activation_token, editable=False)
    activation_token_expiry = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def generate_username_from_email(self):
        """Gera um username único baseado no email"""
        base_username = self.email.split('@')[0]
        username = base_username
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        return username

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.generate_username_from_email()
        super().save(*args, **kwargs)
