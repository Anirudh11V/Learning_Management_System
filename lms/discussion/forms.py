from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        labels = {
            'title': 'Topic Title',
            'content': 'Your Message',
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        labels = {
            'content': 'Your Reply',
        }

        widgets = {
            'content': forms.Textarea(attrs= {'row':4, 'placeholder': 'Write your reply...'}),
        }