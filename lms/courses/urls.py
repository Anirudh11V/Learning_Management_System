from django.urls import path
from . import views

app_name = 'courses'
urlpatterns = [
    path('<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/complete/', views.mark_lesson_completion, 
         name= 'mark_lesson_complete'),
    path('<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/', views.lesson_detail, name= 'lesson_details'),
    path('<slug:course_slug>/', views.course_detail, name= 'course_details'),
    path('', views.course_list, name= 'course_list'),
    
]