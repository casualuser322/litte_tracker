from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from .models import TicketsUser
from .forms import RegisterForm, SignInForm, UserUpdateForm
from tracker.models import Invitation, TrackerGroup


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
            form.add_error(None, "Passwords do not match")
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
                return redirect('group_list')
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = SignInForm()
    
    print(form.errors)
    return render(request, 'accounts/signin.html', {'form': form})

def profile_view(request):
    user = request.user
    if user.is_authenticated:
        if request.method == "POST":
            form = UserUpdateForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                user = form.save(commit=False)
                email = form.cleaned_data.get("email")
                password = form.cleaned_data.get("password")
                if password:
                    user.set_password(password)
                else:
                    password = user.password
                user.save()
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                return redirect("profile")
        else:
            form = UserUpdateForm(instance=user)

        all_invitations = Invitation.objects.filter(
            target_user=user,
            invitation_type='group',
            invitation_status='pending'
        ).select_related("target_group")
        all_groups = {inv.owner: inv.target_group.title for inv in all_invitations}

        print(all_groups)

        return render(request, "accounts/profile.html", {
            "form": form,
            "user": user,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "invitations": all_invitations,
            "invited_to": all_groups,
        })
    else:
        return redirect('signin')

@login_required
def accept_invitation(request, inv_id):
    user = request.user
    if request.method == 'POST':
        invitation = get_object_or_404(
            Invitation, 
            id=inv_id, 
            target_user=request.user
        )
        group = TrackerGroup.objects.get(id=invitation.id)
        
        invitation.status = 'accepted'
        group.members.add(user)

    return redirect(request.META.get("HTTP_REFERER", "profile"))

def decline_invitation(request, inv_id):
    user = request.user

    if request.method == 'POST':
        invitation = get_object_or_404(
            Invitation, 
            id=inv_id, 
            target_user=request.user
        )
        invitation.status = 'declined'
        invitation.save()
    
    return redirect(request.META.get("HTTP_REFERER", "profile"))