from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

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


User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE, related_name= 'profile')
    bio = models.TextField(max_length= 500, blank= True)
    profile_pic = models.ImageField(upload_to= 'profile_pics/', blank= True)

    def __str__(self):
        return f'{self.user.username} Profile'