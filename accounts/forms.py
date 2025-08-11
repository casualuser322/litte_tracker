from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import TicketsUser
from tracker.models import Group, Project, Ticket


class RegisterForm(UserCreationForm):
    class Meta:
        model = TicketsUser
        fields = (
            'email', 
            'username',
            'first_name',
            'last_name',
            'profile_image'
        )

class UserUpdatefrom(forms.ModelForm):
    class Meta:
        model = TicketsUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'profile_image',
            'password'
        )

class SignInForm(forms.ModelForm):
    class Meta:
        model = TicketsUser
        fields = ('email', 'password',)
    
