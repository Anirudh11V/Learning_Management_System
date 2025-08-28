from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import F, Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model, update_session_auth_hash

from .forms import MemberUserChangeForm, MemberUserCreation, UserUpdateForm, ProfileUpdateForm
from .models import Profile, Notification, UserLessonCompletion
from enrollment.models import Enroll
from courses.models import Course, Lesson
# Create your views here.


def register(request):
    if request.method == 'POST':
        form = MemberUserCreation(request.POST)

        if form.is_valid():
            user= form.save()
            login(request, user)
            messages.success(request, "Registration Successful.")
            return redirect('courses:course_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    else:
        form = MemberUserCreation()
    
    context = {'form': form, 'page_title': 'Register'}
    return render(request, 'users/register.html', context)


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data= request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username= username, password= password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome {username} !.")
                return redirect('courses:course_list')
            else:
                messages.error(request, "Invalid credentials.")
            
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
    else:
        form = AuthenticationForm()

    context = {'form': form, 'page_title': 'Login'}
    return render(request, 'users/login.html', context)


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('users:login')

@login_required(login_url= 'users:login')
def profile(request):
    user = request.user
    Profile.objects.get_or_create(user= user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance= user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance= user.profile)

        if 'update_user' in request.POST and user_form.is_valid():
            user_form.save()
            messages.success(request, "Your accounts details are updated successfully.")
            return redirect('users:profile')
        
        elif 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile details are updated successfully.")
            return redirect('users:profile')
        
    else:
        user_form = UserUpdateForm(instance= user)
        profile_form = ProfileUpdateForm(instance= user.profile)

    enrolled_course = Enroll.objects.filter(student= user)
    instructor_course = Course.objects.filter(instructor= user)

    notifications = Notification.objects.filter(user= request.user).order_by('-created_at')

    section = request.GET.get('section', 'info')
    if section == 'notifications':
        notifications.filter(is_read=False).update(is_read=True)

    unread_notifications_count = notifications.filter(is_read=False).count()

    context ={'user_form': user_form, 'profile_form': profile_form, 
              'enrolled_course': enrolled_course, 'instructor_course': instructor_course, 'page_title': 'profile',
              'notifications': notifications, 'unread_notifications_count': unread_notifications_count}
    
    section = request.GET.get('section', 'info')
    if section == 'security':
        template_name = 'partials/profile_security.html'
    elif section == 'courses':
        template_name = 'partials/profile_courses.html'
    elif section == 'notifications':
        template_name = 'partials/profile_notification.html'
    else:
        template_name = 'users/profile.html'
    return render(request, template_name, context)


# @login_required(login_url= 'users:login')
# def student_dashboard(request):
#     if not request.user.is_student:
#         messages.warning(request, "This page is only for student.")

#         if request.user.is_instructor:
#             return redirect('users:profile')
#         else:
#             return redirect('courses:course_list')
        
#     enrolled_course = Enroll.objects.filter(student= request.user).select_related('course')

#     context= {'enrolled_course': enrolled_course, 'page_title': 'My Learning Dashboard'}
#     return render(request, 'users/stu_dashboard.html', context)

@login_required
def student_dashboard(request):
    if not request.user.is_student:
        messages.warning(request, "This page is only for students.")
        return redirect('users:profile')
    
    # Base queryset for all of the users enrollments.
    enrollments = Enroll.objects.filter(student= request.user)

    # Subquery to count total lessons foe each course.
    total_lessons_sq = Lesson.objects.filter(
        module__course= OuterRef('course')
    ).values('module__course').annotate(count= Count('id')).values('count')

    # Subquery to count completed lessons for user in each course.
    completed_lesson_sq = UserLessonCompletion.objects.filter(
        student= request.user,
        lesson__module__course= OuterRef('course'),
        is_completed= True,
    ).values('lesson__module__course').annotate(count= Count('id')).values('count')

    # Annotate the main queryset with the count from out aubqueries.
    enrollments = enrollments.annotate(
        total_lessons = Coalesce(Subquery(total_lessons_sq), 0),
        completed_lessons = Coalesce(Subquery(completed_lesson_sq), 0),
    ).select_related('course')

    context= {'enrolled_courses': enrollments, 
              'page_title': 'My Learning Dashboard'}
    return render(request, "users/stu_dashboard.html", context)


@login_required(login_url= 'users:login')
def Instructor_dashboard(request):
    if not request.user.is_instructor:
        messages.warning(request, "This page is only for Instructors.")

        if request.user.is_student:
            return redirect('users:student_dashboard')
        else:
            return redirect('courses:course_list')
        
    instructor_courses = Course.objects.filter(instructor= request.user)

    context = {'instructor_course': instructor_courses, 'page_title': 'Instructor Dashboard'}
    return render(request, 'users/ins_dashboard.html', context)


def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk= pk)
    notification.is_read= True
    notification.save()
    return redirect(notification.get_absolute_url())