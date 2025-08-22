from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from courses.models import Course, Lesson
# Create your models here.


class MemberUser(AbstractUser):
    is_student = models.BooleanField(default= False)
    is_instructor = models.BooleanField(default= False)

    wants_to_be_instructor = models.BooleanField(default= False, verbose_name= 'Instructor Request')

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
    profile_pic = models.ImageField(upload_to= 'profile_pics/', default= 'default.jpg', blank= True)

    def __str__(self):
        return f'{self.user.username} Profile'
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name= 'notifications')
    message = models.CharField(max_length= 500)
    related_course = models.ForeignKey(Course, on_delete= models.CASCADE, null= True, blank= True)
    related_lesson = models.ForeignKey(Lesson, on_delete= models.CASCADE, null= True, blank= True)

    is_read = models.BooleanField(default= False)
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"Notification for {self.user.username} : {self.message}"
    
    def absolute_url(self):
        if self.related_lesson:
            return reverse('courses:lesson_details', args=[self.related_lesson.module.course.slug,
                                                           self.related_lesson.module.slug, 
                                                           self.related_lesson.slug])
        elif self.related_course:
            return reverse('courses:course_details', args=[self.related_course.slug])
        
        return '#'
    

class UserLessonCompletion(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= 'lesson_completion')

    lesson = models.ForeignKey(Lesson, on_delete= models.CASCADE, related_name= 'user_completions')
    is_completed = models.BooleanField(default= False)
    completed_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        unique_together= ('student', 'lesson')
        ordering = ['completed_at']
        verbose_name_plural = 'User Lesson Completions'

    def __str__(self):
        return f'{self.student.username} completed {self.lesson.title}'