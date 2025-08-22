from django.contrib import admin
from enrollment.models import Enroll
from users.models import UserLessonCompletion

# Register your models here.
@admin.register(Enroll)
class EnrollAdmin(admin.ModelAdmin):
    list_display= ['student', 'course', 'enrolled_at', 'completed_at', 'completion_date']
    list_filter= ['completed_at', 'course', 'student']
    search_fields = ['course__title', 'student__username']
    raw_id_fields= ['student', 'course']


@admin.register(UserLessonCompletion)
class UserLessonCompletionAdmin(admin.ModelAdmin):
    list_display= ['student', 'lesson', 'is_completed', 'completed_at']
    list_filter= ['student', 'lesson__module__course', 'is_completed']
    search_fields= ['student__username', 'lesson__title']
    raw_id_fields= ['student', 'lesson']