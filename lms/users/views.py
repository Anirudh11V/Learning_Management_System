from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import IntegrityError

from .forms import MemberUserChangeForm, MemberUserCreation
from enrollment.models import Enroll
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
    context ={'user': request.user, 'page_title': 'profile'}
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