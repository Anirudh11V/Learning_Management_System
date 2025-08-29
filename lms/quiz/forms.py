from django import forms
from django.db.models.base import Model
from .models import  Quiz, Question, Answer

from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'duration_minutes', 'pass_percentage', 'is_published']
        labels = {
            'title': 'Quiz Title',
            'description': 'Description',
            'duration_minutes': 'Time Limit (in minutes)',
            'pass_percentage': 'Passing Score (%)',
            'is_piblished': 'Make the quiz available to students',
        }
        widgets= {
        'description': TinyMCE(),
        }

        help_texts = {
            'duration_minutes': 'Leave blank for no time limit. ',
            'pass_percentage': 'The minimum score a student needs to pass.',
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'marks']
        labels = {
            'text': 'Question Text',
            'question_type': 'Type of question',
            'marks': 'Points for correct answer',
        }
        widgets= {
            'text': forms.Textarea(attrs= {'rows': 4}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        labels = {
            'text': 'Answer Text',
            'is_correct': 'Is this the correct answer?',
        }
        widgets={
            'text': forms.Textarea(attrs= {'rows': 4}),
        }
    
    def __init__(self, *args, question= None, **kwargs):
        self.question = question
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        is_correct = cleaned_data.get("is_correct")

        if is_correct and self.question and self.question.question_type in ['mcq', 'true_false']:
            existing_correct = self.question.answers.filter(is_correct= True).exclude(pk= self.instance.pk)
            if existing_correct.exists():
                raise ValidationError("Only one correct answer is allowed for this question type.")
        return cleaned_data


class AnswerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj) -> str:
        return obj.text


class UserAnswerForm(forms.Form):
    answer = AnswerChoiceField(
        queryset= Answer.objects.none(),
        widget= forms.RadioSelect,
        empty_label= None,
        required= True,
    )
    def __init__(self, *args, question= None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            self.fields['answer'].queryset = question.answers.all()


class ShortAnswerForm(forms.Form):
    answer_text = forms.CharField(
        widget= TinyMCE(),
        label= "Your Answer"
    )