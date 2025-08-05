from django import forms
from django.contrib.auth.forms import UserCreationForm

# from .models import TicketUser


# class TicketUserCreationForms(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = TicketUser
#         fields = ('username', 'email', 'password1', 'password2', 'first_name', 'second_name')

# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = TicketUser
#         fields = ('first_name', 'last_name', 'email', 'phone', 'avatar')