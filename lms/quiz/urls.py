from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # Instructors
    path('lesson/<int:lesson_id>/create/', views.quiz_create, name= 'quiz_create'),
    path('<int:quiz_id>/manage/', views.quiz_manage, name= 'quiz_manage'),
    path('question/<int:question_id>/answers/', views.answer_manage, name= 'answer_manage'),

    # Students
    path('<int:quiz_id>/start/', views.quiz_start, name= 'quiz_start'),
    path('attempt/<int:attempt_id>/question/<int:question_order>/', views.quiz_take, name= 'quiz_take'),
    path('attempt/<int:attempt_id>/results/', views.quiz_results, name= 'quiz_results')
]