from django.urls import path
from .import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name= 'register'),
    path('', views.user_login, name= 'login'),
    path('logout/', views.logout_user, name= 'logout'),
    path('profile/', views.profile, name= 'profile'),
    path('student_dashboard/', views.student_dashboard, name= 'student_dashboard'),
    path('instructor_dashboard/', views.Instructor_dashboard, name= 'instructor_dashboard'),
    path('notifications/read/<int:pk>/', views.mark_notification_as_read, name= 'mark_notification_as_read'),
]