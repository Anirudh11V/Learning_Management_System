from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError

from courses.models import Course
from .models import Enroll
from users.services import notify_new_enrollment

# Create your views here.

@login_required(login_url= 'users:login')
def enroll_course(request, course_slug):
    course = get_object_or_404(Course, slug= course_slug, is_published= True)

    if not request.user.is_student:
        messages.error(request, "Only student can enroll.")
        return redirect('courses:course_details', course_slug= course_slug)
    
    if request.user.is_instructor:
        messages.error(request, "Instructor cant enroll.")
        return redirect('courses:course_details', course_slug= course_slug)
    
    if request.method == 'POST':
        if Enroll.objects.filter(student= request.user, course= course).exists():
            messages.info(request, "You already enrolled in this course.")
            return redirect('courses:course_details', course_slug= course_slug)
        
        try:
            if course.price > 0:
                messages.info(request, f"Payment simulation : please complete payment {course.price} for {course.title}")

            Enroll.objects.create(student= request.user, course= course)
            notify_new_enrollment(request.user, course)
            messages.success(request, f"Successfully enrolled in {course.title}.")
            return redirect('courses:course_details', course_slug= course_slug)
        
        except IntegrityError:
            messages.error(request, "An error occured during enrollment. You might already be enrolled.")
            return redirect('courses:course_details', course_slug= course_slug)
        
        except Exception as e:
            messages.error(request, f"An unexpected error occurred : {e}")
            return redirect('courses:course_details', course_slug= course_slug)
        
    messages.warning(request, "Enrollment can only be initiated by form submission.")
    return redirect('courses:course_details', course_slug= course_slug)