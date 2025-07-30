from django.urls import path
from . import views

app_name = "enrollment"

urlpatterns = [
    path('enroll/<slug:course_slug>/', views.enroll_course, name= "enroll_course")
]