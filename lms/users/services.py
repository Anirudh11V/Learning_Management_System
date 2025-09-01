from .models import Notification, MemberUser
from courses.models import Course, Lesson
from enrollment.models import Enroll


def create_notification(user_id, message, related_course= None, related_lesson= None):
    Notification.objects.create(
        user_id= user_id,
        message= message,
        related_course= related_course,
        related_lesson= related_lesson,
    )


def notify_new_lesson(new_lesson, course):
    enrolled_user = [course_enrollment.student for course_enrollment in Enroll.objects.filter(course= course)]
    message = f"A new lesson '{new_lesson.title}' has been added to this course '{course.title}'."
    for user in enrolled_user:
        create_notification(user= user, message= message, related_lesson= new_lesson)


def notify_new_enrollment(student, course):
    message = f"A new student '{student.username}' has been enrolled in your course '{course.title}'."
    create_notification(user_id= course.instructor.id, message= message, related_course= course)


def notify_admin_insrtuctor_request(user):
    admins = MemberUser.objects.filter(is_superuser= True)
    message = f"New instructor request from user '{user.username}'. Please review and approve in the admin panel."
    for a in admins:
        create_notification(user_id= a, message= message)