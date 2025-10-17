from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from tracker.models import Invitation

from .forms import RegisterForm, SignInForm, UserUpdateForm
from .models import TicketsUser


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)

            if "profile_image" in request.FILES:
                user.profile_image = request.FILES["profile_image"]
            user.save()
            return redirect("signin")
        else:
            form.add_error(None, "Passwords do not match")
            print(form.errors)
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def signin_view(request):
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("group_list")
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = SignInForm()

    print(form.errors)
    return render(request, "accounts/signin.html", {"form": form})


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
            invitation_type="group",
            invitation_status="pending",
        ).select_related("target_group")
        all_groups = {
            inv.owner: inv.target_group.title for inv in all_invitations
        }

        print(all_groups)

        return render(
            request,
            "accounts/profile.html",
            {
                "form": form,
                "user": user,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "invitations": all_invitations,
                "invited_to": all_groups,
            },
        )
    else:
        return redirect("signin")


@login_required
def accept_invitation(request, inv_id):
    user = request.user
    if request.method == "POST":
        invitation = get_object_or_404(Invitation, id=inv_id, target_user=user)
        group = invitation.target_group
        if user not in group.members.all():
            group.members.add(user)

        invitation.invitation_status = "accepted"
        invitation.save()

    return redirect(request.META.get("HTTP_REFERER", "profile"))


def decline_invitation(request, inv_id):
    user = request.user

    if request.method == "POST":
        invitation = get_object_or_404(Invitation, id=inv_id, target_user=user)
        invitation.status = "declined"
        invitation.save()

    return redirect(request.META.get("HTTP_REFERER", "profile"))


def user_view(request, pk):
    viewing_user = get_object_or_404(TicketsUser, id=pk)

    return render(
        request, "accounts/user_view.html", {"viewing_user": viewing_user}
    )


def logout_(request):
    logout(request)
    return redirect("signin")
