from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import TicketsUser


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    password2 = forms.CharField(label='Confirm your password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))
    profile_image = forms.ImageField(required=False, label='Upload your profile photo')

    class Meta:
        model = User
        fields = ('email', 'username')

    def clean_password2(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data.get('password2')
    

class SignInForm(forms.ModelForm):
    email = forms.EmailInput(attrs={'placeholder': 'Enter your email..'})
    password = forms.CharField(
        label='Enter your password..',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password..'})
    )

    class Meta:
        model = User
        fields = ('email', 'password')
    
