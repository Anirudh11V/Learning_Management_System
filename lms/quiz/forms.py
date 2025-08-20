from django import forms
from .models import  Quiz, Question, Answer


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


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        labels = {
            'text': 'Answer Text',
            'is_correct': 'Is this the correct answer?',
        }


class UserAnswerForm(forms.Form):
    answer = forms.ModelChoiceField(
        queryset= Answer.objects.none(),
        widget= forms.RadioSelect,
        empty_label= None,
        required= True,
    )
    def __init__(self, *args, question= None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            self.fields['answer'].queryset = question.answers.all()