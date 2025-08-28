from django.contrib import admin
from quiz.models import Quiz, Question, Answer, QuizAttempt, UserAnswer

# Register your models here.

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class QuestionInline(admin.StackedInline):
    model = Question
    inlines = [AnswerInline]
    extra = 1

class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ('question', 'selected_answer', 'short_answer_text', 'is_correct_manual', 'graded_at')

    fields = ('question', 'selected_answer', 'short_answer_text', 'is_correct_manual', 'graded_at')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'duration_minutes', 'pass_percentage', 'is_published', 'created_at']
    list_filter = ['is_published', 'lesson__module__course']
    search_fields = ['title', 'lesson__title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'question_type', 'marks', 'order']
    list_filter = ['quiz', 'question_type']
    search_fields = ['text']
    inlines = [AnswerInline]
    raw_id_fields = ['quiz']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['question__quiz', 'is_correct']
    search_fields = ['text']
    raw_id_fields = ['question']


@admin.action(description= "Regrade selected attempts")
def regrade_selected_attempts(modeladmin, request, queryset):
    for attempt in queryset:
        attempt.recalculate_and_save()
    modeladmin.message_user(request, f"{queryset.count()} attempts have been successfully regraded.")

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'total_marks', 'is_completed', 'passed', 'started_at', 'completed_at']
    list_filter = ['is_completed', 'passed', 'student', 'quiz__lesson__module__course']
    search_fields = ['student__username', 'quiz__title']
    readonly_fields = ['score', 'total_marks', 'started_at', 'completed_at', 'passed']
    inlines = [UserAnswerInline]
    actions = [regrade_selected_attempts]


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_answer', 'short_answer_text', 'is_correct_manual']
    list_filter = ['question__quiz', 'is_correct_manual', 'attempt__student']
    search_fields = ['short_answer_text', 'question__text', 'attempt__student__username']
    raw_id_fields = ['attempt', 'question', 'selected_answer']