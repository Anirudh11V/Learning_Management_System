from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

from django.contrib.auth import get_user_model
from .models import MemberUser, Profile
from .services import notify_admin_insrtuctor_request

class MemberUserCreation(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MemberUser
        fields = UserCreationForm.Meta.fields + ('email', 'is_student', 'is_instructor')
    
    def save(self, commit= True):
        user = super().save(commit= False)
        user.is_student = True
        user.is_instructor = False

        if self.cleaned_data.get('is_instructor'):
            user.wants_to_be_instructor = True
            user.is_student = False

        if commit:
            user.save()
            if user.wants_to_be_instructor:
                notify_admin_insrtuctor_request(user)
        return user
    

class MemberUserChangeForm(UserChangeForm):
    class Meta:
        model = MemberUser
        fields = '__all__'


User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_pic']