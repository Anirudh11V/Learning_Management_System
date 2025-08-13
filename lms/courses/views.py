from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Course, Module, Lesson
from .forms import CourseForm
from enrollment.models import Enroll, UserLessonCompletion

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db import IntegrityError
from django.utils import timezone
from django.contrib import messages
from django.utils.text import slugify
# Create your views here.


def course_list(request):
    category_slug = request.GET.get('category')
    courses = Course.objects.filter(is_published= True)
    categories = Category.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug= category_slug)
        courses = courses.filter(category= category)
    else:
        category = None
    
    context= {'courses': courses, "categories": categories, 'selected_category': category, "page_title": 'All Courses'}
    return render(request, 'courses/course_list.html', context)

@login_required(login_url= 'users:login')
def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug= course_slug, is_published= True)
    modules = course.modules.prefetch_related('lesson').all()
    is_enrolled = False

    if request.user.is_authenticated and request.user.is_student:
        is_enrolled = Enroll.objects.filter(student= request.user, course= course).exists()

    context= {'course': course, 'modules': modules, 'is_enrolled': is_enrolled, 'page_title': course.title}
    return render(request, 'courses/course_detail.html', context)


@login_required(login_url= 'users:login')
def lesson_detail(request, course_slug, module_slug, lesson_slug):

    # print(f"course_slug : '{course_slug}'")
    # print(f"module_slug : '{module_slug}'")
    # print(f"lesson_slug : '{lesson_slug}'")
    # print("-" * 30)

    # try:
    course = get_object_or_404(Course, slug= course_slug, is_published= True)
    #     print(f"DEBUG : Found course : {course.title} (ID: {course.id})")
    # except Http404:
    #     print(f"ERROR : Course not found with slug: '{course_slug}' or not published")
    #     raise

    # try:
    module = get_object_or_404(Module, course= course, slug= module_slug)
    #     print(f"DEBUG : Found module : {module.title} (ID: {module.id})")
    # except Http404:
    #     print(f"ERROR : Course not found with slug: '{module_slug}' or not published")
    #     raise

    # try:
    lesson = get_object_or_404(Lesson, module= module, slug= lesson_slug, is_published= True)
    #     print(f"DEBUG : Found lesson : {lesson.title} (ID: {lesson.id})")
    # except Http404:
    #     print(f"ERROR : Course not found with slug: '{lesson_slug}' or not published")
    #     raise

    # print("-" * 30)

    if not request.user.is_student:
        return render(request, 'courses/access_denied.html', 
                        {'msg': 'only students can access'}, status= 403)
    
    is_enrolled = Enroll.objects.filter(student= request.user, course= course).exists()
    if not is_enrolled:
        return render(request, 'courses/access_denied.html', 
                        {'messages': 'You must enroll to view.'}, status= 403)
    
    lesson_completion, created = UserLessonCompletion.objects.get_or_create(
        student= request.user, lesson= lesson, defaults= {'is_completed': False}
    )

    context= {'course': course, 'module': module, 'lesson': lesson, 'lesson_completion': lesson_completion, 'page_title': lesson.title}
    return render(request, 'courses/lesson_detail.html', context)


@login_required(login_url= 'users:login')
def mark_lesson_completion(request, course_slug, module_slug, lesson_slug):
    if request.method == 'POST':
        course= get_object_or_404(Course, slug= course_slug, is_published= True)
        module= get_object_or_404(Module, course= course, slug= module_slug)
        lesson = get_object_or_404(Lesson, module= module, slug= lesson_slug, is_published=True)

    if not request.user.is_student:
        return redirect(request, 'courses/access_denied.html', 
                        {'messages': 'only students can mark lesson'}, status= 403)
    
    is_enrolled = Enroll.objects.filter(student= request.user, course= course).exists()
    if not is_enrolled:
        return redirect(request, 'courses/access_denied.html', 
                        {'messages': 'You must enroll to view.'}, status= 403)
    
    try:
        lesson_completion, created = UserLessonCompletion.objects.get_or_create(
            student= request.user, lesson= lesson,
        )
        if not lesson_completion.is_completed:
            lesson_completion.is_completed= True
            lesson_completion.completed_at= timezone.now()
            lesson_completion.save()
            messages.success(request, 'lesson marked as complete.')

    except IntegrityError:
        pass

        return redirect('courses:lesson_details', course_slug= course_slug, module_slug= module_slug, lesson_slug= lesson_slug)
    
    return redirect('courses:lesson_details', course_slug= course_slug, module_slug= module_slug, lesson_slug= lesson_slug)


@login_required(login_url= 'users:login')
def course_create(request):
    if not request.user.is_instructor:
        messages.error(request, 'You are not authorized to create course.')
        return redirect('users:instructor_dashboard')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            new_course = form.save(commit= False)
            new_course.instructor = request.user
            new_course.slug = slugify(new_course.title)
            new_course.save()
            messages.success(request, f"Course '{new_course.title}' created successfully.")
            return redirect('users:instructor_dashboard')
        
        else:
            messages.error(request, 'Please correct the errors.')

    else:
        form = CourseForm()

    context = {'form': form, 'page_title': 'Create New Course'}
    return render(request, 'courses/course_form.html', context)


@login_required(login_url= 'users:login')
def  course_update(request, course_slug):
    course = get_object_or_404(Course, slug= course_slug)
    if course.instructor != request.user:
        messages.error(request, 'You are not authorized to edit this course.')
        return redirect('users:instructor_dashboard')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance= course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated successfully.")
            return redirect('users:instructor_dashboard')
        else:
            messages.error(request, 'Please correct the errors.')

    else:
        form = CourseForm(instance= course)

    context = {'form': form, 'course': course, 'page_title': f'Edit Course: {course.title}'}
    return render(request, 'courses/course_form.html', context)


@login_required(login_url= 'users:login')
def course_delete(request, course_slug):
    course = get_object_or_404(Course, slug= course_slug)
    if course.instructor != request.user:
        messages.error(request, 'You are not authorized to delete this course.')
        return redirect('users:instructor_dashboard')
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f"Course '{course.title}' deleted successfully.")
        return redirect('users:instructor_dashboard')
    
    context = {'course': course, 'page_title': f'Delete Course: {course.title}'}
    return render(request, 'courses/course_confirm_delete.html', context)