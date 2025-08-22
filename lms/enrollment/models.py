from django.db import models
from django.conf import settings

from courses.models import Course, Lesson
from users.models import UserLessonCompletion

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
    
    def get_progress_percentage(self):
        total_lessons = Lesson.objects.filter(module__course= self.course).count()
        if total_lessons == 0:
            return 0
        
        completed_lessons_count = UserLessonCompletion.objects.filter(
            student= self.student,
            lesson__module__course= self.course,
            is_completed = True,
            ).count()
        return (completed_lessons_count / total_lessons) * 100 
    

