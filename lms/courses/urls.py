from django.urls import path
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.course_list, name= 'course_list'),
    path('<slug:course_slug>/', views.course_detail, name= 'course_details'),

    # COURSE CRUD URL.
    path('create/', views.course_create, name= 'course_create'),
    path('<slug:course_slug>/update/', views.course_update, name= 'course_update'),
    path('<slug:course_slug>/delete/', views.course_delete, name= 'course_delete'),

    # MODULE CRUD URL.
    path('<slug:course_slug>/module/create/', views.module_create, name= 'module_create'),
    path('<slug:course_slug>/module/<slug:module_slug>/update/',
         views.module_update, name= 'module_update'),
    path('<slug:course_slug>/module/<slug:module_slug>/delete/',
         views.module_delete, name= 'module_delete'),

    # LESSON CRUD URL.
    path('<slug:course_slug>/module/<slug:module_slug>/lesson/create/', views.lesson_create, name= 'lesson_create'),
    path('<slug:course_slug>/module/<slug:module_slug>/lesson/<slug:lesson_slug>/update/',
         views.lesson_update, name= 'lesson_update'),
    path('<slug:course_slug>/module/<slug:module_slug>/lesson/<slug:lesson_slug>/delete/',
         views.lesson_delete, name= 'lesson_delete'),

    path('<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/complete/', views.mark_lesson_completion, 
         name= 'mark_lesson_complete'),
    path('<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/', views.lesson_detail, name= 'lesson_details'),
    
    
    # path('<slug:course_slug>/manage/', views.course_content_manage, name= 'course_content_manage'),
    
]