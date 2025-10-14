import json

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from accounts.models import TicketsUser

from .decorators import group_access_required, project_access_required
from .forms import (
    CommentForm,
    GroupForm,
    ProjectForm,
    SecureAttachmentForm,
    TicketForm,
)
from .models import (
    Invitation,
    Project,
    SubTask,
    Ticket,
    TrackerGroup,
)


@login_required
def group_list(request):
    user = request.user

    owned_groups = user.owned_groups.all()
    member_groups = user.attached_groups.all()

    return render(
        request,
        "groups/groups_main.html",
        {
            "owned_groups": owned_groups,
            "member_groups": member_groups,
        },
    )


@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()

            emails = request.POST.get("emails", "")

            if emails:
                for email in emails.split(","):
                    email = email.strip()

                    target_user = get_object_or_404(TicketsUser, email=email)

                    Invitation.objects.create(
                        owner=request.user,
                        target_user=target_user,
                        target_group=group,
                        invitation_type="group",
                    )

            group.members.add(request.user)
            form.save_m2m()
            messages.success(request, "Group is created!")
            return redirect("group_list")
    else:
        form = GroupForm()

    return render(
        request,
        "groups/groups_create.html",
        {
            "form": form,
        },
    )


@login_required
@group_access_required
def group_view(request, group_id, group=None):
    projects = (
        group.projects.select_related("owner")
        .prefetch_related("members", "tickets")
        .order_by("-created_at")
    )

    all_members = group.members.all()
    if not all_members.filter(id=group.owner.id).exists():
        all_members = list(all_members) + [group.owner]

    return render(
        request,
        "groups/groups_view.html",
        {
            "group": group,
            "projects": projects,
            "members": all_members,
            "user_can_edit": request.user == group.owner,
            "user_is_member": request.user in group.members.all(),
        },
    )


@login_required
@group_access_required
def delete_group_member(request, group_id, pk, group=None):
    user = request.user
    group = get_object_or_404(TrackerGroup, id=group_id)

    if user.id == group.owner.id and pk in group.attached_groups.all():
        group.members.remove(pk)

    return redirect(request.META.get("HTTP_REFERER", reverse("group_view")))


@login_required
def leave_group_member(request, group_id):
    user = request.user
    group = get_object_or_404(TrackerGroup, id=group_id)

    if group.owner != user:
        if group.members.filter(id=user.id).exists():
            group.members.remove(user)
            messages.success(request, f"You left the group {group.title}.")
        else:
            messages.warning(request, "You are not a member of this group.")
    else:
        messages.error(request, "Group owners cannot leave their own group.")

    return redirect(request.META.get("HTTP_REFERER", reverse("group_list")))


@login_required
@group_access_required
def delete_project(request, project_id):
    user = request.user
    project = get_object_or_404(Project, id=project_id)

    if user.id == project.owner.id:
        project.delete()

    return redirect(request.META.get("HTTP_REFERER", reverse("group_view")))


def user_email_autocomplete(request):
    query = request.GET.get("q", "")
    users = TicketsUser.objects.filter(email__icontains=query)[:10]
    results = [{"id": u.id, "email": u.email} for u in users]

    return JsonResponse(results, safe=False)


@login_required
@group_access_required
def send_invitation(request, group_id, group=None):
    current_user = request.user
    emails = request.POST.get("emails", "").strip()

    if emails:
        if group.owner.id == current_user.id:
            for email in [e.strip() for e in emails.split(",") if e.strip()]:
                try:
                    user = TicketsUser.objects.get(email=email)
                    Invitation.objects.create(
                        owner=current_user,
                        target_user=user,
                        target_group=group,
                        invitation_type="group",
                    )
                except TicketsUser.DoesNotExist:
                    pass  # TODO
        else:
            messages.error(
                request, "You don't have permission to send invitation"
            )

    return redirect(
        request.META.get(
            "HTTP_REFERER", reverse("group_view", args=[group_id])
        )
    )


@login_required
@group_access_required
def group_delete(request, group_id, pk, group=None):
    if request.method == "POST":
        if group.owner == request.user:
            group.delete()
            messages.success(request, "Group deleted successfully!")
        else:
            messages.error(
                request, "You do not have permission to delete this group."
            )

    return redirect("group_list")


@login_required
def project_list(request):
    user = request.user
    projects = user.projects.filter(members=user.id)
    owned_projects = user.owned_projects.all()

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects,
            "owned_projects": owned_projects,
        },
    )


@login_required
@group_access_required
def create_project(request, group_id, group=None):
    user = request.user
    if request.method == "POST":
        form = ProjectForm(request.POST)
        emails = request.POST.get("emails", "").split(",")

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = user
            project.attached_group = group
            project.save()
            project.members.add(user)

            for email in emails:
                email = email.strip()
                if not email:
                    continue
                coworker = TicketsUser.objects.filter(email=email).first()
                if coworker:
                    project.members.add(coworker)

            messages.success(request, "Project is created!")
            return redirect("project_list")
    else:
        form = ProjectForm()

    return render(request, "projects/create_project.html", {"form": form})


@login_required
@project_access_required
def project_details(request, project_id, project=None):
    tickets = project.tickets.all()

    statuses = [
        {"key": "open", "label": "Open", "badge_class": "bg-secondary"},
        {
            "key": "in_progress",
            "label": "In Progress",
            "badge_class": "bg-warning text-dark",
        },
        {
            "key": "testing",
            "label": "Testing",
            "badge_class": "bg-info text-dark",
        },
        {"key": "done", "label": "Done", "badge_class": "bg-success"},
        {
            "key": "closed",
            "label": "Closed",
            "badge_class": "bg-dark text-white",
        },
    ]

    priority = [
        {"key": "low", "label": "Low", "badge_class": "badge-success"},
        {"key": "medium", "label": "Medium", "badge_class": "badge-warning"},
        {"key": "high", "label": "High", "badge_class": "badge-danger"},
    ]

    return render(
        request,
        "projects/project_details.html",
        {
            "project": project,
            "tickets": tickets,
            "statuses": statuses,
            "priority": priority,
        },
    )


@login_required
def ticket_list(request):
    user = request.user
    user_tickets = Ticket.objects.filter(assigne=user.id)

    return render(
        request, "tickets/ticket_list.html", {"user_tickets": user_tickets}
    )


@require_POST
@csrf_protect
@project_access_required
def update_task_status(request, project_id, project=None):
    try:
        data = json.loads(request.body)
        task_id = data.get("task_id")
        status = data.get("status")
        task = get_object_or_404(Ticket, id=task_id, project_id=project_id)

        valid_statuses = [choice[0] for choice in Ticket.STATUS_CHOICES]
        if status not in valid_statuses:
            return JsonResponse(
                {"success": False, "error": "Invalid status"}, status=400
            )

        task.status = status
        task.save()

        return JsonResponse(
            {
                "success": True,
                "status": task.status,
                "status_display": task.get_status_display(),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_POST
def add_subtask(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        SubTask.objects.create(ticket=ticket, text=request.POST.get("subtask"))

    return redirect(request.META.get("HTTP_REFERER", reverse("ticket_detail")))


@require_POST
@login_required
@project_access_required
def update_task_ajax(request, project_id, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, project_id=project_id)

    data = json.loads(request.body)
    new_status = data.get("status")

    valid_statuses = ["todo", "in_progress", "in_review", "done"]
    if new_status not in valid_statuses:
        return JsonResponse(
            {"success": False, "error": "Invalid status"}, status=400
        )

    ticket.status = new_status
    ticket.save()

    return JsonResponse(
        {
            "success": True,
            "status": ticket.status,
            "status_display": ticket.get_status_display(),
        }
    )


@login_required
@project_access_required
def ticket_detail(request, project_id, ticket_id, project):  # TODO decompose
    ticket = get_object_or_404(Ticket, id=ticket_id)

    comments = ticket.comments.all()
    attachments = ticket.attachments.all()
    subtasks = ticket.subtasks.all()

    SubTaskFormSet = modelformset_factory(
        SubTask,
        fields=("text", "is_done"),
        extra=0,
        widgets={
            "text": forms.TextInput(attrs={"class": "form-control"}),
            "is_done": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        },
    )

    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Ticket updated successfully!")
            return redirect("ticket_detail", ticket_id=ticket.id)
        else:
            form = TicketForm(instance=ticket, project=ticket.project)

        if "add_comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                messages.success(request, "Comment added!")
                return redirect("ticket_detail", ticket_id=ticket.id)
        else:
            comment_form = CommentForm()

        if "add_attachment" in request.POST:
            attachment_form = SecureAttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.ticket = ticket
                attachment.uploaded_by = request.user
                attachment.save()
                messages.success(request, "File attached!")
                return redirect("ticket_detail", ticket_id=ticket.id)
        else:
            attachment_form = SecureAttachmentForm()

        if "update_subtasks" in request.POST:
            formset = SubTaskFormSet(request.POST, queryset=subtasks)
            if formset.is_valid():
                formset.save()
                messages.success(request, "Subtasks updated!")
                return redirect("ticket_detail", ticket_id=ticket.id)
        else:
            formset = SubTaskFormSet()

        if "add_subtask" in request.POST:
            new_text = request.POST.get("new_subtask")
            if new_text:
                SubTask.objects.create(ticket=ticket, text=new_text)
                messages.success(request, "Subtask added!")
                return redirect("ticket_detail", ticket_id=ticket.id)

    else:
        comment_form = CommentForm()
        attachment_form = SecureAttachmentForm()
        formset = SubTaskFormSet(queryset=subtasks)

    return render(
        request,
        "tickets/ticket_detail.html",
        {
            "project": project,
            "ticket": ticket,
            "comments": comments,
            "attachments": attachments,
            "comment_form": comment_form,
            "formset": formset,
            "attachment_form": attachment_form,
            "PRIORITY_CHOICES": Ticket.PRIORITY_CHOICES,
        },
    )


@login_required
@project_access_required
def create_ticket(request, project_id, project):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.project = project
            ticket.creator = request.user
            ticket.save()
            messages.success(request, "Ticket created!")
            return redirect("project_details", project_id=project.id)
    else:
        form = TicketForm()

    return render(
        request,
        "tickets/create_ticket.html",
        {
            "form": form,
            "project": project,
            "today": timezone.now().date(),
        },
    )


@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        ticket_form = TicketForm(request.POST, instance=ticket)
        if ticket_form.is_valid():
            ticket_form.save()
            messages.success(request, "Ticket is updated")

            return redirect("ticket_detail", ticket_id=ticket.id)

    else:
        form = TicketForm()
        form.fields["assigne"].queryset = ticket.project.members.all()

    return render(
        request,
        "tickets/ticket_form.html",
        {
            "form": ticket_form,
            "ticket": ticket,
        },
    )


def index(request):
    user = request.user
    if user.is_authenticated:
        return redirect("group_list")
    else:
        return redirect("register")
