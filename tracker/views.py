from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Attachment, Comment, Project, Ticket
from .forms import AttachmentForm, CommentForm, ProjectForm, TicketForm


@login_required
def project_list(request):
    projects = request.user.projects.all()
    owned_projects = request.user.owned_projects.all()

    return render(request, 'tracker/project_list.html', {
        'projects': projects,
        'owned_projects': owned_projects,
    })

@login_required
def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user not in project.members.all() and request.user != project.owner:
        return redirect('project_list')
    
    tickets = project.tickets.all()

    return render(request, 'tickets/project_details.html', {
        'project': project,
        'tickets': tickets,
    })

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()
            messages.success(request, 'Project is created!')
    else:
        form = ProjectForm()
    
    return render(request, 'tickets/project_form.html', {
        'form': form,
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
    return redirect('project_list')