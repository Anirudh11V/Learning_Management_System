from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MemberUser


class MemberUserCreation(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MemberUser
        fields = UserCreationForm.Meta.fields + ('email', 'is_student', 'is_instructor')

    def clean_is_instructor(self):
        if self.cleaned_data.get('is_instructor'):
            raise ValueError("You cant register as instructor.")
        return False
    
    def save(self, commit= True):
        user = super().save(commit= False)
        user.is_student = True
        user.is_instructor = False
        if commit:
            user.save()
        return user
    

class MemberUserChangeForm(UserChangeForm):
    class Meta:
        model = MemberUser
        fields = '__all__'