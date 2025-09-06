from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Course, Module, Lesson, Review
from .forms import CourseForm, ModuleForm, LessonForm, CommentForm, CategoryForm, ReviewForm
from enrollment.models import Enroll
from quiz.models import QuizAttempt, Quiz
from users.models import UserLessonCompletion
from users.task import task_notify_new_lesson

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db import IntegrityError
from django.db.models import Max
from django.utils import timezone
from django.contrib import messages
from django.utils.text import slugify
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
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
    review_form = None
    user_review = None

    reviews = course.reviews.all().select_related('student')

    if request.user.is_authenticated and request.user.is_student:
        is_enrolled = Enroll.objects.filter(student= request.user, course= course).exists()

        # Check if the user has already reviewed this course. 
        user_review = reviews.filter(student= request.user).first()

        if is_enrolled and not user_review:
            if request.method == 'POST':
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    new_review = review_form.save(commit= False)
                    new_review.course = course
                    new_review.student = request.user
                    new_review.save()
                    messages.success(request, "Thank you for your review!")
                    return redirect('courses:course_details', course_slug= course.slug)
                
                else:
                    review_form = ReviewForm()

    context= {'course': course, 'modules': modules, 'is_enrolled': is_enrolled, 
              'reviews': reviews, 'review_form': review_form, 'user_review': user_review, 'page_title': course.title}
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
    """
    Lesson nagivation...
    """
    lesson_in_module = module.lesson.all().order_by('order')

    lesson_list = list(lesson_in_module)
    current_lesson_index = lesson_list.index(lesson)

    previous_lesson = None
    if current_lesson_index > 0:
        previous_lesson = lesson_list[current_lesson_index - 1]

    next_lesson = None
    if current_lesson_index < len(lesson_list) - 1:
        next_lesson = lesson_list[current_lesson_index + 1]

    # lesson navigation ends
        
    """
    Comments...
    """
    comments = lesson.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit= False)
            new_comment.lesson = lesson
            new_comment.author = request.user
            new_comment.save()
            return redirect('courses:lesson_details', 
                            course_slug= course.slug, module_slug= module.slug, lesson_slug= lesson.slug)
    
    else:
        form = CommentForm()

    context= {'course': course, 'module': module, 'lesson': lesson, 'lesson_completion': lesson_completion, 
              'page_title': lesson.title, 'previous_lesson': previous_lesson, 'next_lesson': next_lesson,
              'form': form, 'comments': comments}
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
        c_form = CategoryForm(request.POST)
        form = CourseForm(request.POST, request.FILES)

        if 'create_course' in request.POST and form.is_valid():
            new_course = form.save(commit= False)
            new_course.instructor = request.user
            new_course.slug = slugify(new_course.title)
            new_course.save()
            messages.success(request, f"Course '{new_course.title}' created successfully.")
            return redirect('users:instructor_dashboard')
        
        elif 'course_category' in request.POST and c_form.is_valid():
            new_category = c_form.save(commit= False)
            new_category.instructor = request.user
            new_category.slug = slugify(new_category.Name)
            new_category.save()
        
        else:
            messages.error(request, 'Please correct the errors.')

    else:
        c_form = CategoryForm()
        form = CourseForm()

    context = {'form': form, 'c_form': c_form, 'page_title': 'Create New Course'}
    return render(request, 'courses/course_form.html', context)


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def test_func(self):
        # Check if the current user is the instructor of the course.
        return self.get_object().instructor == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, "Course updated succcessfully!")
        return super().form_valid(form)
    

class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('users:instructor_dashboard')

    def test_func(self):
         # Check if the current user is the instructor of the course.
        return self.get_object().instructor == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, "Course deleted succcessfully!")
        return super().form_valid(form)

# ------------- COURSE CRUD ENDS ------------------------------------------------.

@login_required(login_url= 'users:login')
def course_manage(request, course_slug):
    course = get_object_or_404(Course, slug= course_slug)

    if not request.user.is_instructor or course.instructor != request.user:
        messages.error(request, "You are not authoried to manage this course.")
        return redirect("users:instructor_dashboard")
    
    enrollments = Enroll.objects.filter(course= course).select_related('student')

    quiz_attempts = QuizAttempt.objects.filter(
        quiz__lesson__module__course= course
    ).select_related('student', 'quiz').order_by('-started_at')

    # Find all quizzes in this course that contains short answer question
    quizzes_to_grade = Quiz.objects.filter(
        lesson__module__course= course,
        questions__question_type= 'short_answers',
    ).distinct()

    context= {'course': course, 'enrollments': enrollments, 'quiz_attempts': quiz_attempts,
              'quizzes_to_grade': quizzes_to_grade, 'page_title': f"Manage: {course.title}"}

    return render(request, 'courses/course_manage.html', context)

# ------------- MODULE CRUD ------------------------------------------------.

class ModuleCreateView(LoginRequiredMixin, CreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug= self.kwargs['course_slug'])
        return context
    
    def form_valid(self, form):
        course = get_object_or_404(Course, slug= self.kwargs['course_slug'])
        form.instance.course = course

        if course.instructor != self.request.user:
            messages.error(self.request, "you are not authorized to add module in this course.")
            return redirect('courses:course_list')
        
        max_order = course.modules.aggregate(Max('order'))['order__max']
        form.instance.order = (max_order or 0) + 1

        messages.success(self.request, "Module added successfully.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.course.get_absolute_url()
    

class ModuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'
    slug_url_kwarg = 'module_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context
    
    def test_func(self):
        return self.get_object().course.instructor == self.request.user
    
    def get_success_url(self):
        return self.object.course.get_absolute_url()


class ModuleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Module
    template_name = 'courses/module_confirm_delete.html'
    slug_url_kwarg = 'module_slug'

    def test_func(self):
        return self.get_object().course.instructor == self.request.user
    
    def get_success_url(self):
        return self.object.course.get_absolute_url()
# ------------- MODULE CRUD ENDS------------------------------------------------.

# ------------- LESSON CRUD STARTS------------------------------------------------.

class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug= self.kwargs['course_slug'])
        context['module'] = get_object_or_404(Module, slug= self.kwargs['module_slug'])
        return context
 
    def form_valid(self, form):
        module = get_object_or_404(Module, slug= self.kwargs['module_slug'])
        form.instance.module = module

        # check permission
        if module.course.instructor != self.request.user:
            messages.error(self.request, "You are not authorized to add lessons to this course.")
            return redirect('courses:course_list')
        
        # Automatically calculate and set the order for the new lesson.
        max_order = module.lesson.aggregate(Max('order'))['order__max']
        form.instance.order = (max_order or 0) + 1
        
        messages.success(self.request, "Lesson created successfully.")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect to the course detail page after creation
        return self.object.module.course.get_absolute_url()
    

class LessonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    slug_url_kwarg = 'lesson_slug'  # to find lesson by its own slug

    def get_context_data(self, **kwargs):
        # This adds the course and module for the template
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.module.course
        context['module'] = self.object.module
        return context

    def test_func(self):
        # Check if the current user is the instructor
        return self.get_object().module.course.instructor == self.request.user
    
    def get_success_url(self):
        return self.object.module.course.get_absolute_url()
    

class LessonDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Lesson
    template_name = 'courses/lesson_confirm_delete.html'
    slug_url_kwarg = 'lesson_slug'

    def test_func(self):
        return self.get_object().module.course.instructor == self.request.user

    def get_success_url(self):
        return self.object.module.get_absolute_url()
# ------------- LESSON CRUD ENDS------------------------------------------------.