from django.db import models
from django.conf import settings
from courses.models import Lesson
from django.core.exceptions import ValidationError
from django.utils import timezone

from users.models import MemberUser
# Create your models here.

class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete= models.CASCADE, related_name= 'quiz')

    title = models.CharField(max_length= 200)
    description = models.TextField(blank= True, null =True)
    duration_minutes = models.PositiveIntegerField(blank= True, null =True, help_text= "optional: time limit")
    pass_percentage = models.PositiveIntegerField(default= 0, help_text= "minimum percent")
    is_published= models.BooleanField(default= False)
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (Lesson : {self.lesson.title})"
    
    def get_total_marks(self):
        return self.questions.aggregate(total_marks= models.Sum('marks'))['total_marks'] or 0
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete= models.CASCADE, related_name= 'questions')

    text = models.TextField(blank=False, null= False)
    marks = models.PositiveIntegerField(default= 1)
    question_type = models.CharField(max_length= 30, choices= [
        ('mcq', 'Multiple Choice Question'),
        ('true_false', 'True / False'),
        ('short_answers', 'Short Answers'),
    ], default= 'mcq' )

    order = models.PositiveIntegerField(default= 0)

    class Meta:
        ordering = ['order']
        unique_together = ('quiz', 'order')

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}...."
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete= models.CASCADE, related_name= 'answers')

    text = models.TextField(blank=False, null= False)
    is_correct = models.BooleanField(default= False)

    class Meta:
        verbose_name_plural = "Answers"
    
    def __str__(self):
        return f'{self.text} (correct : {self.is_correct})'
    
class QuizAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= 'qui_attempts',
                                limit_choices_to= {'is_student': True})
    
    quiz = models.ForeignKey(Quiz, on_delete= models.CASCADE, related_name="attempts")
    score = models.PositiveIntegerField(default= 0)
    total_marks = models.PositiveIntegerField(default= 0)
    started_at = models.DateTimeField(auto_now_add= True)
    completed_at = models.DateTimeField(blank= True, null= True)
    is_completed = models.BooleanField(default= False)
    passed = models.BooleanField(default= False)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        status = "completed" if self.is_completed else "In progress"
        return f"{self.student.username}'s attempt on {self.quiz.title} ({status})"
    
    def calculate_score(self):
        score = 0
        self.total_marks = self.quiz.get_total_marks() or 0

        # Query all answers for this attempt.
        answers = self.user_answers.all().select_related('question')

        for user_answer in answers:
            if user_answer.question.question_type in ['mcq', 'true_false']:
                if user_answer.selected_answer and user_answer.selected_answer.is_correct:
                    score += user_answer.question.marks
            elif user_answer.question.question_type == 'short_answers':
                if user_answer.is_correct_manual:
                    score += user_answer.question.marks

        self.score= score


    def evaluate_pass_status(self):
        if self.is_completed and self.total_marks > 0:
            percentage = (self.score / self.total_marks) * 100
            self.passed = percentage >= self.quiz.pass_percentage
        else:
            self.passed = False

    def complete_attempts(self):
        self.is_completed= True
        self.completed_at= timezone.now()
        self.calculate_score()
        self.evaluate_pass_status()
        self.save()

    def recalculate_and_save(self): 
        """Recalculate score and pass status, then saves the attempt."""
        self.calculate_score()
        self.evaluate_pass_status()
        self.save()   


class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete= models.CASCADE, related_name= 'user_answers')
    question = models.ForeignKey(Question, on_delete= models.CASCADE, related_name= 'user_responses')
    selected_answer = models.ForeignKey(Answer, on_delete= models.SET_NULL, 
                                        null= True, blank= True, related_name= 'user_selections')
    short_answer_text = models.TextField(blank= True, null= True)
    is_correct_manual = models.BooleanField(default= False)
    graded_at = models.DateTimeField(null= True, blank= True)

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        if self.question.question_type in ['mcq', 'true_false'] and self.selected_answer:
            return f"{self.attempt.student.username}'s answer to {self.question.id}: {self.selected_answer.text}"
        elif self.question.question_type == 'short_answer' and self.short_answer_text:
            return f"{self.attempt.student.username}'s short answer to {self.question.id}: {self.short_answer_text[:50]}."
        return f"{self.attempt.student.username}'s answer to {self.question.id}"