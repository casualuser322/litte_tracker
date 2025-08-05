from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
# from .forms import TicketUserCreationForms, ProfileUpdateForm


# def register(request):
#     if request.method == 'POST':
#         form = TicketUserCreationForms(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
            
#             return redirect('project_list')
#     else:
#         form = TicketUserCreationForms()
    
#     return render(request, 'accounts/register.html')

# @login_required
# def profile(request):
#     if request.method == 'POST':
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()

#             return redirect('profile')
#     else:
#         form = ProfileUpdateForm(isinstance=request.user)
    
#     return render(request, 'accounts/profile.html')

def register(request):
    return render(request, 'accounts/register.html')