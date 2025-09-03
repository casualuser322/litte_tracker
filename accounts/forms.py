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
            'password1',
            'password2',
        )

class SignInForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)

class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label='Password'
    )

    class Meta:
        model = TicketsUser
        fields = [
            'email', 
            'username', 
            'first_name', 
            'last_name', 
            'password', 
            'profile_image'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        else:
            password = user.password
        if commit:
            user.save()
        return user
