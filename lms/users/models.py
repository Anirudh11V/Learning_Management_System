from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils.translation import gettext_lazy as _
# Create your models here.


class MemberUser(AbstractUser):
    is_student = models.BooleanField(default= False)
    is_instructor = models.BooleanField(default= False)

    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(null= True, blank= True)
    avatar = models.ImageField(null= True, blank= True)
    phone = models.CharField(max_length= 10, null= True, blank= True)


    def __str__(self):
        return self.username
