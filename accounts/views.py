from django.shortcuts import render, redirect
from .forms import RegisterForm, SignInForm
from django.contrib.auth.models import User
from .models import TicketsUser

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile = user.userprofile
            profile.profile_image = form.cleaned_data.get('profile_image')
            profile.save()

            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def sigin_view(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            session_content = form.save()
            
            return redirect('project_list')
    
    else:
        form = SignInForm()
    
    return render(request, 'accounts/signin.html', {'form': form})

def profile_view(request):
    if request.method == 'POST':
        form = 0
    
    else:
        form = 1

    return render(request, 'accounts/profile.html', {'form': form})
