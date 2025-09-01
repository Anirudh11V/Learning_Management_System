from celery import shared_task

from .services import create_notification
from courses.models import Course, Lesson
from enrollment.models import Enroll


@shared_task
def task_notify_new_lesson(lesson_id, course_id):
    """Asynchronous task to send notifications when a new lesson is added."""
    try:
        lesson = Lesson.objects.get(id= lesson_id)
        course = Course.objects.get(id= course_id)
        enrolled_users = Enroll.objects.filter(course= course).values_list('student', flat= True)
        message = f"A new lesson '{lesson.title}' has been added to the course '{course.title}'." 

        for user_id in enrolled_users:
            create_notification(user_id=user_id, message= message, related_lesson= lesson)
        return f"Notifications sent for lesson {lesson.title}"
    
    except(Lesson.DoesNotExist, Course.DoesNotExist):
        return "Lesson or Course not found."