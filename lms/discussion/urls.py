from django.urls import path
from . import views

app_name = 'discussion'

urlpatterns = [
    path('course/<slug:course_slug>/', views.post_list, name= 'post_list'),
    path('post/<int:post_id>/', views.post_detail, name= 'post_detail'),
]