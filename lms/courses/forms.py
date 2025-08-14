from django import forms
from . models import Course, Module, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'is_published']
        labels = {
            'title': 'Course title',
            'description': 'Course Description',
            'price': 'Price(Rs)',
            'is_published': 'Publish this course?',
        }

        widgets = {
            'description': forms.Textarea(attrs= {'rows': 4}),
            'price': forms.NumberInput(attrs= {'step': '0.01'}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        labels = {
            'title': 'Module Title',
            'description': 'Module Description',
            'order': 'Module Ordering (eg. 1, 2, 3, ...)',
        }

        widgets = {
            'description': forms.Textarea(attrs= {'rows':4}),
            'order': forms.NumberInput(attrs= {'placeholder': 'Enter a number'}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'text_content', 'video_url', 'file_upload', 'is_published', 'order']
        labels = {
            'title': 'Lesson Title',
            'text_content': 'Lesson Text Content',
            'video_url': 'Video URL',
            'file_upload': 'Upload a file',
            'is_published': 'Publish this Lesson?',
            'order': 'Lesson ordering (eg. 1, 2, 3, ...)',
        }

        widgets = {
            'text_content': forms.Textarea(attrs= {'rows': 8}),
            'order': forms.NumberInput(attrs= {'placeholder': 'Enter a number'}),
        }