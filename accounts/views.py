from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from .models import TicketsUser
from .forms import RegisterForm, SignInForm, UserUpdateForm

class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label='Password'
    )

    class Meta:
        model = TicketsUser
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'profile_image']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  

            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
            user.save()
            return redirect('signin')
        else:
            print(form.errors)
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def signin_view(request):   # TODO process validation ui
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('project_list')
            else:
                form.add_error(None, "Invalid email or password.")
        else:
            print(form.errors)
    else:
        form = SignInForm()
    
    return render(request, 'accounts/signin.html', {'form': form})

def profile_view(request):
    user = request.user

    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")
            if password:
                user.set_password(password)
            user.save()
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form})
