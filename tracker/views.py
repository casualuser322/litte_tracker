import json

from django import forms 
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.templatetags.static import static
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.forms import modelformset_factory

from accounts.models import TicketsUser
from .models import \
    Attachment, Comment, Invitation, TrackerGroup, Project, Ticket, SubTask
from .forms import \
    AttachmentForm, CommentForm, GroupForm, \
        SubTaskForm, ProjectForm, TicketForm


@login_required
def group_list(request):
    user = request.user

    owned_groups = user.owned_groups.all()          
    member_groups = user.attached_groups.all()

    return render(request, 'groups/groups_main.html', {
        'owned_groups': owned_groups,
        'member_groups': member_groups,
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
                        invitation_type='group',
                    )

            group.members.add(request.user)
            form.save_m2m()
            messages.success(request, 'Group is created!')
            return redirect('group_list')
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

def delete_group_member(request, group_id, pk):
    admini = request.user
    group = get_object_or_404(TrackerGroup, id=group_id)

    if admini.id == group.owner.id:
        group.members.remove(pk)

    return redirect(request.META.get("HTTP_REFERER", "group_view"))

def leave_group_member(request, group_id):
    user = request.user
    group = get_object_or_404(TrackerGroup, id=group_id)

    if group.owner == user:
        messages.error(request, "Group owners cannot leave their own group.")
        return redirect(request.META.get("HTTP_REFERER", "group_list"))

    if group.members.filter(id=user.id).exists():
        group.members.remove(user)
        messages.success(request, f"You left the group {group.title}.")
    else:
        messages.warning(request, "You are not a member of this group.")

    return redirect(request.META.get("HTTP_REFERER", "group_list"))

def delete_project(request, project_id):
    admini = request.user
    project = get_object_or_404(Project, id=project_id)

    if admini.id == project.owner.id:
        project.delete()

    return redirect(request.META.get("HTTP_REFERER", "group_view"))


def user_email_autocomplete(request):
    query = request.GET.get("q", "")
    users = TicketsUser.objects.filter(email__icontains=query)[:10]
    results = [{"id": u.id, "email": u.email} for u in users]

    return JsonResponse(results, safe=False)\

def send_invitation(request, group_id):
    emails = request.POST.get("emails", "").strip()
    group = get_object_or_404(TrackerGroup, id=group_id)

    if emails:
        for email in [e.strip() for e in emails.split(",") if e.strip()]:
            try:
                user = TicketsUser.objects.get(email=email)
                Invitation.objects.create(
                    owner=request.user,
                    target_user=user,
                    target_group=group,
                    invitation_type="group",
                )
            except TicketsUser.DoesNotExist:
                pass

    return redirect(request.META.get("HTTP_REFERER", "group_view"))

@login_required
def group_delete(request, pk):
    group = get_object_or_404(TrackerGroup, id=pk)

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
    projects = request.user.projects.filter(members=request.user.id)
    owned_projects = request.user.owned_projects.all()
    print(projects)

    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'owned_projects': owned_projects,
    })

@login_required
def create_project(request, group_id):
    user = request.user
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        emails = request.POST.get("emails", "").split(",")

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = user
            project.attached_group = get_object_or_404(TrackerGroup, id=group_id)
            project.save()
            project.members.add(user)

            for email in emails:
                email = email.strip()
                if not email:
                    continue
                coworker = TicketsUser.objects.filter(email=email).first()
                if coworker:
                    project.members.add(coworker)

            messages.success(request, 'Project is created!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user not in project.members.all() and request.user != project.owner:
        return redirect('project_list')

    tickets = project.tickets.all()

    statuses = [
        {"key": "open", "label": "Open", "badge_class": "bg-secondary"},
        {"key": "in_progress", "label": "In Progress", "badge_class": "bg-warning text-dark"},
        {"key": "testing", "label": "Testing", "badge_class": "bg-info text-dark"},
        {"key": "done", "label": "Done", "badge_class": "bg-success"},
        {"key": "closed", "label": "Closed", "badge_class": "bg-dark text-white"},
        {"key": "low", "label": "Low", "badge_class": "badge-success"},
        {"key": "medium", "label": "Medium", "badge_class": "badge-warning"},
        {"key": "high", "label": "High", "badge_class": "badge-danger"},
    ]


    context = {
        "project": project,
        "tickets": tickets,
        "statuses": statuses,
    }

    return render(request, 'projects/project_details.html', context)

@csrf_exempt
def update_task_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        task_id = data.get('task_id')
        status = data.get('status')
        try:
            task = Ticket.objects.get(id=task_id)
            task.status = status
            task.save()
            return JsonResponse({'success': True})
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False}, status=404)
    return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def add_subtask(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    user = request.user

    if request.method == 'POST':
        subtask = SubTask.objects.create(
            ticket=ticket,
            text=request.POST.get('subtask')
        )

    return redirect(request.META.get("HTTP_REFERER", "ticket_detail"))

@require_POST
def update_task_ajax(request, ticket_id, pk):
    try:
        task = SubTask.objects.get(pk=pk, ticket_id=ticket_id)  # Если SubTask привязан к Ticket
    except SubTask.DoesNotExist:
        return JsonResponse({"success": False, "error": "Task not found"}, status=404)

    data = json.loads(request.body)
    task.is_done = data.get("completed", False)
    task.save()

    return JsonResponse({"success": True, "is_done": task.is_done})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.user not in ticket.project.members.all() and request.user != ticket.project.owner:
        return redirect('project_list')
    
    comments = ticket.comments.all()
    attachments = ticket.attachments.all()
    subtasks = ticket.subtasks.all()
    project = get_object_or_404(Project, id=ticket.project.id)

    SubTaskFormSet = modelformset_factory(
        SubTask,
        fields=("text", "is_done"),
        extra=0,
        widgets={
            "text": forms.TextInput(attrs={"class": "form-control"}),
            "is_done": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
    )

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            form = TicketForm(instance=ticket, project=ticket.project)


        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                messages.success(request, 'Comment added!')
                return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            comment_form = CommentForm()
        
        if 'add_attachment' in request.POST:
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.ticket = ticket
                attachment.uploaded_by = request.user
                attachment.save()
                messages.success(request, 'File attached!')
                return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            attachment_form = AttachmentForm()

        if 'update_subtasks' in request.POST:
            formset = SubTaskFormSet(request.POST, queryset=subtasks)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Subtasks updated!')
                return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            formset = SubTaskFormSet()

        if 'add_subtask' in request.POST:
            new_text = request.POST.get("new_subtask")
            if new_text:
                SubTask.objects.create(ticket=ticket, text=new_text)
                messages.success(request, 'Subtask added!')
                return redirect('ticket_detail', ticket_id=ticket.id)
            

    else:
        comment_form = CommentForm()
        attachment_form = AttachmentForm()
        formset = SubTaskFormSet(queryset=subtasks)

    
    return render(request, 'tickets/ticket_detail.html', {
        'project': project,
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'formset': formset,
        'PRIORITY_CHOICES': Ticket.PRIORITY_CHOICES,
    })

@login_required
def create_ticket(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user not in project.members.all() and request.user != project.owner:
        return redirect('project_list')

    if request.method == 'POST':
        form = TicketForm(request.POST, project=project)  
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.project = project
            ticket.creator = request.user
            ticket.save()
            messages.success(request, "Ticket created!")
            return redirect('project_details', project_id=project.id)
        else:
            print(form.errors)
    else:
        form = TicketForm(project=project)

    return render(request, 'tickets/create_ticket.html', {
        'form': form,
        'project': project,
        'today': timezone.now().date(),
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