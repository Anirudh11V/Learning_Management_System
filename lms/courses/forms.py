from django import forms
from . models import Course


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