from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import MemberUserChangeForm, MemberUserCreation, UserUpdateForm, ProfileUpdateForm, PasswordChangeForm
from .models import Profile
from enrollment.models import Enroll
from courses.models import Course
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
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance= user)
        profile_form = ProfileUpdateForm(request.POST, instance= user.profile)
        password_form = PasswordChangeForm(data= request.POST, user= user )

        if 'update_user' in request.POST and user_form.is_valid():
            user_form.save()
            messages.success(request, "Your accounts details are updated successfully.")
            return redirect('users:profile')
        
        elif 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile details are updated successfully.")
            return redirect('users:profile')
        
        elif 'change_password' in request.POST and password_form.is_valid():
            new_password = password_form.save()
            update_session_auth_hash(request, new_password)
            messages.success(request, "Your password was successfully updated.")
            return redirect('users:profile')
        
    else:
        user_form = UserUpdateForm(instance= user)
        profile_form = ProfileUpdateForm(instance= user.profile)
        password_form = PasswordChangeForm(user= user)

    enrolled_course = Enroll.objects.filter(student= user)
    instructor_course = Course.objects.filter(instructor= user)

    context ={'user_form': user_form, 'profile_form': profile_form, 'password_form': password_form, 
              'enrolled_course': enrolled_course, 'instructor_course': instructor_course, 'page_title': 'profile'}
    return render(request, 'users/profile.html', context)


@login_required(login_url= 'users:login')
def student_dashboard(request):
    if not request.user.is_student:
        messages.warning(request, "This page is only for student.")

        if request.user.is_instructor:
            return redirect('users:profile')
        else:
            return redirect('courses:course_list')
        
    enrolled_course = Enroll.objects.filter(student= request.user).select_related('course')

    context= {'enrolled_course': enrolled_course, 'page_title': 'My Learning Dashboard'}
    return render(request, 'users/stu_dashboard.html', context)


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