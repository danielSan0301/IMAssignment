from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(blank=True, unique = True)
    verified = models.BooleanField(default = False)
 
class Token(models.Model):
    token = models.CharField(max_length=256, unique=True)
    temp_user_id = models.IntegerField(unique = True, null=True)
    date = models.DateTimeField(null = True)
    
class TemporalUser(models.Model):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=True)
    password = models.BinaryField(_('password'), max_length=256)
    iv = models.BinaryField(max_length=128)
   
    
