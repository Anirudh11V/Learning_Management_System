from django.db import models
from django.conf import settings

from courses.models import Course, Lesson

# Create your models here.

class Enroll(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE,
                                limit_choices_to= {'is_student': True}, related_name= 'course_enrollment')
    
    course = models.ForeignKey(Course, on_delete= models.CASCADE, related_name= 'enrollments')
    enrolled_at = models.DateTimeField(auto_now_add = True)
    completed_at = models.BooleanField(default= False)
    completion_date = models.DateTimeField(null= True, blank= True)

    class Meta:
        unique_together= ('student', 'course')
        ordering = ['-enrolled_at']

    def __str_(self):
        return f'{self.student.username} enrolled in {self.course.title}'
    
    def get_progess_percentage(self):
        total_lesson = self.course.modules.aggregate(total_lesson = models.Count('lesson'))['total_lesson']
        if not total_lesson:
            return 0
        
        complete_lesson = self.userlessoncompletion_set.filter(is_compeleted = True).count()
        return (complete_lesson / total_lesson) * 100 if total_lesson > 0 else 0
    

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