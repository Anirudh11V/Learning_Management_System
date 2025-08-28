from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from .models import Quiz, Question, Answer, QuizAttempt, UserAnswer
from .forms import QuizForm, QuestionForm, AnswerForm, UserAnswerForm, ShortAnswerForm
from courses.models import Lesson
from enrollment.models import Enroll

# Create your views here.

def is_imstructor_of_lesson(user, lesson):
    return lesson.module.course.instructor == user


@login_required
def quiz_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, id= lesson_id)
    if not is_imstructor_of_lesson(request.user, lesson):
        messages.error(request, 'You are not authorized to add a quiz to this lesson.')
        return redirect('courses:course_details', course_slug= lesson.module.course.slug)
    
    if hasattr(lesson, 'quiz'):
        messages.info(request, 'A quiz already exists for this lesson. You can manage it instead.')
        return redirect('quiz:quiz_manage', quiz_id= lesson.quiz.id)
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            new_quiz = form.save(commit= False)
            new_quiz.lesson = lesson
            new_quiz.save()
            messages.success(request, f"Quiz '{new_quiz.title}' created. Now add some questions.")
            return redirect('quiz:quiz_manage', quiz_id= lesson.quiz.id)
        
    else:
        form = QuizForm()

    context = {'form': form, 'lesson': lesson, 'page_title': 'Create Quiz'}
    return render(request, 'quiz/quiz_form.html', context)


@login_required
def quiz_manage(request, quiz_id):
    quiz = get_object_or_404(Quiz, id= quiz_id)
    if not is_imstructor_of_lesson(request.user, quiz.lesson):
        messages.error(request, 'You are not authorized to manage this quiz.')
        return redirect('courses:course_details', course_slug= quiz.lesson.module.course.slug)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            new_question = question_form.save(commit= False)
            new_question.quiz = quiz
            max_order = quiz.questions.aggregate(Max('order'))['order__max']
            new_question.order = (max_order or 0) + 1
            new_question.save()
            messages.success(request,"New Question added.")
            return redirect('quiz:quiz_manage', quiz_id= quiz.id)
        
    else:
        question_form = QuestionForm()

    questions = quiz.questions.all().prefetch_related('answers')
    context = {
        'quiz': quiz, 'question_form': question_form, 'questions': questions, 'page_title': f'Manage Quiz: {quiz.title}',
    }
    return render(request, 'quiz/quiz_manage.html', context)


@login_required
def answer_manage(request, question_id):
    question = get_object_or_404(Question, id= question_id)
    quiz = question.quiz
    if not is_imstructor_of_lesson(request.user, quiz.lesson):
        messages.error(request, 'You are not authorized to manage answers for this quiz.')
        return redirect('courses:course_details', course_slug= quiz.lesson.module.course.slug)
    
    if request.method == 'POST':
        answer_form = AnswerForm(request.POST, question= question)
        if answer_form.is_valid():
            new_answer = answer_form.save(commit= False)
            new_answer.question = question
            new_answer.save()
            messages.success(request,"New answers added.")
            return redirect('quiz:answer_manage', question_id= question.id)
        
    else:
        answer_form = AnswerForm()

    answers = question.answers.all()
    context = {
        'question': question, 'answers': answers, 'answer_form': answer_form, 
        'page_title': f'Manage Answer for Q{question.order}.' 
    }
    return render(request, 'quiz/answer_manage.html', context)


@login_required
def quiz_start(request, quiz_id):
    quiz = get_object_or_404(Quiz, id= quiz_id, is_published= True)
    course = quiz.lesson.module.course

    is_enrolled = Enroll.objects.filter(student= request.user, course= course).exists()
    if not request.user.is_student or not is_enrolled:
        messages.error(request, "You must be an enrolled student to take this quiz.")
        return redirect('course:lesson_details', 
                        course_slug= course.slug, module_slug= quiz.lesson.module.slug,lesson_slug= quiz.lesson.slug)
    
    if request.method == 'POST':
        attempt = QuizAttempt.objects.create(student= request.user, quiz= quiz)
        return redirect('quiz:quiz_take', attempt_id= attempt.id, question_order= 1)
    
    context = {'quiz': quiz}
    return render(request, 'quiz/quiz_start_confirm.hmtl', context)


@login_required
def quiz_take(request, attempt_id, question_order):
    attempt = get_object_or_404(QuizAttempt, id= attempt_id)

    if attempt.student != request.user or attempt.is_completed:
        raise PermissionDenied("You don't have permission to view this page.")
    
    question = get_object_or_404(Question, quiz= attempt.quiz, order= question_order)

    form = None
    if request.method == 'POST':
        if question.question_type in ['mcq', 'true_false']:
            form =  UserAnswerForm(request.POST, question= question)
            if form.is_valid():
                selected_answer = form.cleaned_data['answer']
                UserAnswer.objects.update_or_create(
                    attempt= attempt,
                    question= question,
                    defaults= {'selected_answer': selected_answer},
                )

        elif question.question_type == 'short_answers':
            form = ShortAnswerForm(request.POST)
            if form.is_valid():
                answer_text = form.cleaned_data['answer_text']
                UserAnswer.objects.update_or_create(
                    attempt= attempt,
                    question= question,
                    defaults= {'short_answer_text': answer_text}
                )

        if form and form.is_valid():
            next_question = Question.objects.filter(quiz= attempt.quiz, 
                                                    order__gt= question_order).order_by('order').first()

        if next_question:
            return redirect('quiz:quiz_take', attempt_id= attempt.id, question_order= next_question.order)
        else:
            attempt.complete_attempts()
            return redirect('quiz:quiz_results', attempt_id= attempt.id)
        
    else:
        if question.question_type in ['mcq', 'true_false']:
            form = UserAnswerForm(question= question)
        elif question.question_type == 'short_answers':
            form = ShortAnswerForm()

    context= {'attempt': attempt, 'question': question, 'form': form, 'page_title': f"Question {question.order}"}
    return render(request, 'quiz/quiz_take.html', context)


@login_required
def quiz_results(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id= attempt_id)

    if attempt.student != request.user:
        raise PermissionDenied("You can't view there results.")
    
    percentage_score = 0
    if attempt.total_marks > 0:
        percentage_score = (attempt.score / attempt.total_marks) * 100
    
    context= {'attempt': attempt, 'percentage_score':percentage_score, 'page_title': f"Result for {attempt.quiz.title}"}
    return render(request, 'quiz/quiz_results.html', context)


@login_required
def grade_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id= quiz_id)
    course = quiz.lesson.module.course

    if request.user != course.instructor:
        messages.error(request, "You are not authorized to grade this quiz.")
        return redirect('users:instructor_dashboard')
    
    # Find all ungraded short answers.
    ungraded_answers = UserAnswer.objects.filter(
        attempt__quiz= quiz,
        question__question_type= 'short_answers',
        graded_at__isnull= True,
    ).select_related('question', 'attempt__student')

    context= {'quiz': quiz, 'ungraded_answers': ungraded_answers, 'page_title': f"Grade Short Answer for {quiz.title}"}
    return render(request, "quiz/grade_quiz.html", context)


@login_required
def mark_answer_correct(request, user_answer_id):
    if request.user == 'POST':
        user_answer = get_object_or_404(UserAnswer, id= user_answer_id)
        quiz = user_answer.attempt.quiz
        course = quiz.lesson.module.course

        if request.user != course.instructor:
            messages.error(request, "You are not authorized to perform this action.")
            return redirect('users:instructor_dashboard')
        
        user_answer.is_correct_manual = True
        user_answer.graded_at = timezone.now()
        user_answer.save()

        user_answer.attempt.recalculate_and_save()
        messages.success(request, "Amswer marked as correct and score updated.")
        return redirect("quiz:grade_quiz", quiz_id= quiz.id)
    
    return redirect('users:instructor_dashboard')