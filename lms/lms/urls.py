"""
URL configuration for lms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # users app.
    path('accounts/', include('users.urls')),
    path('', include('users.urls')),

    # Enrollment app.
    path('enroll/', include('enrollment.urls')),

    # courses app.
    path('courses', include('courses.urls')),

    # Quiz app.
    path('quiz/', include('quiz.urls')),
    
    # Discussion app.
    path('discussion/', include('discussion.urls')),

    # tinymce
    path('tinymce/', include('tinymce.urls')),

    # Django password reset urls.
    path('accounts/password_reset/', 
         auth_view.PasswordResetView.as_view(template_name= 'users/password_reset_form.html'),
         name= 'password_reset'),
        
    path('accounts/password_reset/done/', 
         auth_view.PasswordResetDoneView.as_view(template_name= 'users/password_reset_done.html'),
         name= 'password_reset_done'),

    path('accounts/reset/<uidb64>/<token>/', 
         auth_view.PasswordResetConfirmView.as_view(template_name= 'users/password_reset_confirm.html'),
         name= 'password_reset_confirm'),

    path('accounts/reset/done/', 
         auth_view.PasswordResetCompleteView.as_view(template_name= 'users/password_reset_complete.html'),
         name= 'password_reset_complete'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root= settings.STATICFILES_DIRS)