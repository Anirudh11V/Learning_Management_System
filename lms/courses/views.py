from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Course, Module, Lesson
from .forms import CourseForm, ModuleForm, LessonForm
from enrollment.models import Enroll, UserLessonCompletion
from users.services import notify_new_lesson

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db import IntegrityError
from django.db.models import Max
from django.utils import timezone
from django.contrib import messages
from django.utils.text import slugify
# Create your views here.

# ------------- COURSE LIST/DETAIL-VIEW ------------------------------------------------.

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

# ---------------------------------------------------------------------------------------------------.

# ------------- LESSON DETAIL-VIEW ------------------------------------------------.

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
                        {'msg': 'You must enroll to view.'}, status= 403)
    
    lesson_completion, created = UserLessonCompletion.objects.get_or_create(
        student= request.user, lesson= lesson, defaults= {'is_completed': False}
    )

    lesson_in_module = module.lesson.all().order_by('order')

    lesson_list = list(lesson_in_module)
    current_lesson_index = lesson_list.index(lesson)

    previous_lesson = None
    if current_lesson_index > 0:
        previous_lesson = lesson_list[current_lesson_index - 1]

    next_lesson = None
    if current_lesson_index < len(lesson_list) - 1:
        next_lesson = lesson_list[current_lesson_index + 1]

    context= {'course': course, 'module': module, 'lesson': lesson, 'lesson_completion': lesson_completion, 
              'page_title': lesson.title, 'previous_lesson': previous_lesson, 'next_lesson': next_lesson}
    return render(request, 'courses/lesson_detail.html', context)

# ----------------------------------------------------------------------------------------.

# ------------- MARKING LESSON AS COMPLETED ------------------------------------------------.

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

        return redirect('courses:lesson_details', 
                        course_slug= course_slug, module_slug= module_slug, lesson_slug= lesson_slug)
    
    return redirect('courses:lesson_details', 
                    course_slug= course_slug, module_slug= module_slug, lesson_slug= lesson_slug)

# ---------------------------------------------------------------------------------------------------.

# ------------- COURSE CRUD STARTS ------------------------------------------------.

@login_required(login_url= 'users:login')
def course_create(request):                 # Course creation.
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
def course_update(request, course_slug):    # Course edit/updating.
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
def course_delete(request, course_slug):     # Course deletion.
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

# ------------- COURSE CRUD ENDS ------------------------------------------------.

# @login_required(login_url= 'users:login')
# def course_content_manage(request):
    # course = get_object_or_404(Course, slug= course_slug)

    # if course.instructor != request.user:
    #     messages.error(request, 'You are not authorized to manage this course.')
    #     return redirect('users:instructor_dashboard')
    
    # modules = Module.objects.filter(course= course).order_by('order')

    # for i in modules:
    #     i.lesson_sorted = i.lesson.all().order_by('order')

    # context = {'course': course, 'modules': modules, 'page_title': f'Manage Content for "{course.title}".'}
    # return render(request, 'courses/partials/instructor_course_management.html')

# ------------- MODULE CRUD ------------------------------------------------.

@login_required(login_url= 'users:login')
def module_create(request, course_slug):     # Module creation.
    course = get_object_or_404(Course, slug= course_slug)
    if course.instructor != request.user:
        messages.error(request, 'You are not authorized to add module to this course.')
        return redirect('users:instructor_dashboard')
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            new_module = form.save(commit= False)
            new_module.course = course
            new_module.slug = slugify(new_module.title)
            new_module.save()
            messages.success(request, f"Module '{new_module.title}' added successfully.")
            return redirect('courses:course_details', course_slug= course.slug)
        
    else:
        form = ModuleForm()

    context= {'form': form, 'course': course, 'page_title': 'Add New Module'}
    return render(request, 'courses/module_form.html', context)

@login_required(login_url= 'users:login')
def module_update(request, course_slug, module_slug):    # Module edit/updating.
    module = get_object_or_404(Module, slug= module_slug, course__slug= course_slug)
    if module.course.instructor != request.user:
        messages.error(request, 'You are not authorized to edit this module.')
        return redirect('courses:course_details', course_slug= module.course.slug)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance= module)
        if form.is_valid():
            form.save()
            messages.success(request, f"Module {module.title} updated successfully.")
            return redirect('courses:course_details', course_slug= module.course.slug)
    
    else:
        form = ModuleForm(instance= module)

    context= {'form': form, 'course': module.course, 'page_title': f'Edit Module: {module.title}'}
    return render(request, 'courses/module_form.html', context)

@login_required(login_url= 'users:login')
def module_delete(request, course_slug, module_slug):    # Module deletion.
    module = get_object_or_404(Module, slug= module_slug, course__slug= course_slug)
    if module.course.instructor != request.user:
        messages.error(request, 'You are not authorized to delete this module.')
        return redirect('courses:course_details', course_slug= module.course.slug)
    
    if request.method == "POST":
        module_title = module.title
        module.delete()
        messages.success(request, f"Module {module.title} deleted successfully.")
        return redirect('courses:course_details', course_slug= module.course.slug)
    
    context = {'course': module.course, 'page_title': f'Delete Module: {module.title}'}
    return render(request, 'courses/module_confirm_delete.html', context)

# ------------- MODULE CRUD ENDS------------------------------------------------.

# ------------- LESSON CRUD STARTS------------------------------------------------.

@login_required(login_url= 'users:login')
def lesson_create(request, course_slug, module_slug):    # Lesson creation.
    course= get_object_or_404(Course, slug= course_slug)
    module= get_object_or_404(Module, course= course, title__iexact= module_slug)
    if course.instructor != request.user:
        messages.error(request, 'You are not authorized to add lesson to this course.')
        return redirect('users:instructor_dashboard')
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            new_lesson = form.save(commit= False)
            new_lesson.module = module
            new_lesson.slug = slugify(new_lesson.title)
            max_order = Lesson.objects.filter(module= module).aggregate(Max('order'))['order__max']
            new_lesson.order = max_order + 1 if max_order is not None else 1
            new_lesson.save()
            
            messages.success(request, f"Lesson '{new_lesson.title}' added successfully.")
            notify_new_lesson(new_lesson, course)
            return redirect('courses:course_details', course_slug= course.slug)
        
    else:
        form = LessonForm()

    context= {'form': form, 'course': course, 'module': module, 'page_title': 'Add New Lesson'}
    return render(request, 'courses/lesson_form.html', context)

@login_required(login_url= 'users:login')
def lesson_update(request, course_slug, module_slug, lesson_slug):   # Lesson edit/updating.
    lesson = get_object_or_404(Lesson, slug= lesson_slug, module__slug= module_slug, module__course__slug= course_slug)
    if lesson.module.course.instructor != request.user:
        messages.error(request, 'You are not authorized to edit this lesson.')
        return redirect('courses:course_details', course_slug= lesson.module.course.slug)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, instance= lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lesson {lesson.title} updated successfully.")
            return redirect('courses:course_details', course_slug= lesson.module.course.slug)
    
    else:
        form = LessonForm(instance= lesson)

    context= {'form': form, 'course': lesson.module.course, 'module': lesson.module,
              'page_title': f'Edit Lesson: {lesson.title}'}
    return render(request, 'courses/lesson_form.html', context)

@login_required(login_url= 'users:login')
def lesson_delete(request, course_slug, module_slug, lesson_slug):   # Lesson deletion.
    lesson = get_object_or_404(Lesson, slug= lesson_slug, module__slug= module_slug, module__course__slug= course_slug)
    if lesson.module.course.instructor != request.user:
        messages.error(request, 'You are not authorized to delete this lesson.')
        return redirect('courses:course_details', course_slug= lesson.module.course.slug)
    
    if request.method == 'POST':
        lesson_title = lesson.title
        lesson.delete()
        messages.success(request, f"Lesson {lesson.title} deleted successfully.")
        return redirect('users:instructor_dashboard')
    
    context = {'course': lesson.module.course, 'page_title': f'Delete Lesson: {lesson.title}',
               'lesson': lesson, 'module': lesson.module}
    return render(request, 'courses/lesson_confirm_delete.html', context)

# ------------- LESSON CRUD ENDS------------------------------------------------.