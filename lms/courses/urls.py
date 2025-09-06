from django.urls import path
from . import views
from .views import (CourseUpdateView, CourseDeleteView, LessonCreateView, LessonUpdateView, LessonDeleteView,
                    ModuleCreateView, ModuleUpdateView, ModuleDeleteView)

app_name = 'courses'
urlpatterns = [
    
    # COURSE CRUD URL.
    path(
        '<slug:course_slug>/manage/', 
        views.course_manage, 
        name= 'course_manage'
        ),
    path(
        'create/', 
        views.course_create, 
        name= 'course_create'
        ),
    path(
        '<slug:slug>/update/', 
        CourseUpdateView.as_view(), 
        name= 'course_update'
        ),
    path(
        '<slug:slug>/delete/', 
        CourseDeleteView.as_view(), 
        name= 'course_delete'
        ),

    # MODULE CRUD URL.
    path(
        '<slug:course_slug>/module/create/',
         ModuleCreateView.as_view(), 
         name= 'module_create'
         ),
    path(
        '<slug:course_slug>/module/<slug:module_slug>/update/',
         ModuleUpdateView.as_view(), 
         name= 'module_update'
         ),
    path(
        '<slug:course_slug>/module/<slug:module_slug>/delete/',
         ModuleDeleteView.as_view(), 
         name= 'module_delete'
         ),

    # LESSON CRUD URL.
    path(
        '<slug:course_slug>/module/<slug:module_slug>/lesson/create/', 
         LessonCreateView.as_view(), 
         name= 'lesson_create'
         ),
    path(
        '<slug:course_slug>/module/<slug:module_slug>/lesson/<slug:lesson_slug>/update/',
         LessonUpdateView.as_view(), 
         name= 'lesson_update'
         ),
    path(
        '<slug:course_slug>/module/<slug:module_slug>/lesson/<slug:lesson_slug>/delete/',
         LessonDeleteView.as_view(), 
         name= 'lesson_delete'
         ),

    path(
        '<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/complete/', 
         views.mark_lesson_completion, 
         name= 'mark_lesson_complete'
         ),
    path(
        '<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/', 
         views.lesson_detail, 
         name= 'lesson_details'
         ),
    
     # main url
    path(
        '<slug:course_slug>/', 
        views.course_detail, 
        name= 'course_details'
        ),
    path(
        '', 
        views.course_list, 
        name= 'course_list'
        ),
    
]