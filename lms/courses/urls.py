from django.urls import path
from . import views

app_name = 'courses'
urlpatterns = [
    path('<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/complete/', views.mark_lesson_completion, 
         name= 'mark_lesson_complete'),
    path('<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/', views.lesson_detail, name= 'lesson_details'),
    path('create/', views.course_create, name= 'course_create'),
    path('<slug:course_slug>/', views.course_detail, name= 'course_details'),
    
    path('', views.course_list, name= 'course_list'),

    
    path('<slug:course_slug>/update/', views.course_update, name= 'course_update'),
    path('<slug:course_slug>/delete/', views.course_delete, name= 'course_delete'),
    
]