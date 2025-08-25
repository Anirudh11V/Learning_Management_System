from django.db import models
from django.conf import settings
from courses.models import Course

# Create your models here.

class Post(models.Model):
    course = models.ForeignKey(Course, on_delete= models.CASCADE, related_name= 'posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= 'posts')

    parent = models.ForeignKey('self', on_delete= models.CASCADE, null= True, blank= True, related_name= 'replies')

    title = models.CharField(max_length= 200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if self.parent:
            return f"Reply by {self.author.username} to {self.parent.title}"
        return f'Post "{self.title}" by {self.author.username}'