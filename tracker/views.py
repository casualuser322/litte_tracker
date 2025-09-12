from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import TicketsUser
from .models import \
    Attachment, Comment, Invitation, TrackerGroup, Project, Ticket
from .forms import \
    AttachmentForm, CommentForm, GroupForm, ProjectForm, TicketForm


@login_required
def group_list(request):
    user = request.user
    owned_groups = user.owned_groups.all()
    groups = TrackerGroup.objects.all()
    return render(request, 'groups/groups_main.html', {
        'groups': groups,
    })

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()

            emails = request.POST.get('emails', '')

            if emails:
                for email in emails.split(','):
                    email = email.strip()
                    try:
                        target_user = TicketsUser.objects.get(email=email)
                    except TicketsUser.DoesNotExist:
                        messages.warning(request, f"User with email {email} not found.")
                        continue

                    Invitation.objects.create(
                        owner=request.user,
                        target_user=target_user,
                        target_group=group,
                        invitation_type='group'
                    )

            group.members.add(request.user)
            form.save_m2m()
            messages.success(request, 'Group is created!')
            return redirect('group_list')
        else:
            print(form.errors)
    else:
        form = GroupForm()
    
    return render(request, 'groups/groups_create.html', {
        'form': form,
    })

@login_required
def group_view(request, group_id):
    try:
        group = TrackerGroup.objects.get(id=group_id)
        projects = group.projects.all()
        members = group.members.all()
        members = members.union(TicketsUser.objects.filter(id=group.owner.id))
        return render(request, "groups/groups_view.html", {
            "group": group,
            "projects": projects,
            "members": members,
            "analogy": static('tracker/img/invalid.png'),
        })
    except TrackerGroup.DoesNotExist:
        return redirect('group_list')

def user_email_autocomplete(request):
    query = request.GET.get("q", "")
    users = TicketsUser.objects.filter(email__icontains=query)[:10]
    results = [{"id": u.id, "email": u.email} for u in users]

    return JsonResponse(results, safe=False)

@login_required
def group_delete(request, pk):
    group = get_object_or_404(TrackerGroup, pk=pk)

    if group.owner != request.user:
        messages.error(
            request,
            "You do not have permission to delete this group."
        )
        return redirect('group_list') 
    if request.method == "POST":
        group.delete()
        messages.success(request, "Group deleted successfully!")
        return redirect('group_list')

    return redirect('group_list')

@login_required
def project_list(request):
    projects = request.user.projects.all()
    owned_projects = request.user.owned_projects.all()

    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'owned_projects': owned_projects,
    })

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.members.add(request.user)
            project.members.add(*form.cleaned_data['members'])
            project.save()
            form.save_m2m()
            messages.success(request, 'Project is created!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create_project.html', {
        'form': form,
    })

@login_required
def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user not in project.members.all() and request.user != project.owner:
        return redirect('project_list')
    
    tickets = project.tickets.all()
    open_tickets = tickets.filter(status='open').all()
    in_progress_tickets = tickets.filter(status='in_progress').all()
    testing_tickets = tickets.filter(status='testing').all()
    done_tickets = tickets.filter(status='done').all()
    closed_tickets = tickets.filter(status='closed').all()

    return render(request, 'projects/project_details.html', {
        'project': project,
        'tickets': tickets,
        # 'open_tickets': open_tickets,
        # 'in_progress_tickets': in_progress_tickets,
        # 'testing_tickets': testing_tickets,
        # 'done_tickets': done_tickets,
        # 'closed_tickets': closed_tickets,
    })

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.user not in ticket.project.members.all() and request.user != ticket.project.owner:
        return redirect('project_list')
    
    comments = ticket.comments.all()
    attachments = ticket.attachments.all()

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                messages.success(request, 'Comment added!')

                return redirect('ticket_detail', ticket_id=ticket.id)
        
        elif 'add_attachment' in request.POST:
            attachment_form = AttachmentForm(request.POST)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.ticket = ticket
                attachment.uploaded_by = request.user
                attachment.save()
                messages.success(request, 'File attached!')

                return redirect('ticket_detail', ticket_id=ticket.id)
        
    else:
        comment_form = CommentForm()
        attachment_form = AttachmentForm()
    
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
    })

@login_required
def create_ticket(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user not in project.members.all() and request.user != project.owner:
        return redirect('project_list')
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.project = project
            ticket.creator = request.user
            ticket.save()
            messages.success("Ticket created!")

            return redirect('project_detail', project_id=project.id)
    
    else:
        form = TicketForm()
        form.fields['assigne'].queryset = project.members.all()
    
    return render(request, 'tickets/ticket_form.html', {
        'form': form,
        'project': project,
    })

@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.user not in ticket.project.members.all() and request.user != ticket.project.owner:
        return redirect('project_list')

    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, isinstance=ticket)
        if ticket_form.is_valid():
            ticket_form.save()
            messages.success(request, "Ticket is updated")
            
            return redirect('ticket_detail', ticket_id=ticket.id)
    
    else:
        form = TicketForm()
        form.fields['assigne'].queryset = ticket.project.members.all()
    
    return render(request, 'tickets/ticket_form.html', {
        'form': ticket_form,
        'ticket': ticket,
    })

def index(request):
    user = request.user
    if user.is_authenticated:
        return redirect('group_list')
    else:
        return redirect('register')