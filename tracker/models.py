from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser


class TrackerGroup(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        'accounts.TicketsUser',
        on_delete=models.CASCADE,
        related_name="owned_groups",
    )    
    members = models.ManyToManyField(
        'accounts.TicketsUser', 
        related_name="attached_groups",
        blank=True
    )
    group_logo = models.ImageField(
        upload_to='group_avatars/',
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        'accounts.TicketsUser',
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    attached_group = models.ForeignKey(
        TrackerGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    members = models.ManyToManyField(
        'accounts.TicketsUser',
        related_name='projects',
        blank=True,
    )

    def __str__(self):
        return self.title

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In progress'),
        ('testing', 'Testing'),
        ('done', 'Done'),
        ('closed', 'Closed')
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ]

    TYPE_CHOICES = [
        ('task', 'Task'),
        ('bug', 'Bug'),
        ('feature', 'Feature'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=None)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="low"
    )
    ticket_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="task"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    due_data = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE, 
        related_name='tickets',
    )
    creator = models.ForeignKey(
        'accounts.TicketsUser',
        on_delete=models.CASCADE,
        related_name='created_tickets',
    )
    assigne = models.ForeignKey(
        'accounts.TicketsUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
    )

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'

class Comment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        'accounts.TicketsUser',
        on_delete=models.CASCADE,
    )
    text = models.TextField(blank=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment from {self.author}, to {self.ticket.title}, at {self.created_at}"

class Attachment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    attached_file = models.FileField(upload_to='ticket_attachments')
    uploaded_by = models.ForeignKey(
        'accounts.TicketsUser',
        on_delete=models.CASCADE,
    )
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Attachment to {self.ticket.title}"

class Invitation(models.Model):
    INVITATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    INVITATION_TYPES_CHOICES = [
        ('group', 'Group'),
        ('project', 'Project'), 
    ]

    owner = models.ForeignKey(
        'accounts.TicketsUser',
        on_delete=models.CASCADE,
        related_name="invitation_owner",
    )
    target_user = models.ForeignKey(
        'accounts.TicketsUser',
        on_delete=models.CASCADE,
        related_name="target_user",
    )
    invitation_type = models.CharField(
        max_length=20,
        choices=INVITATION_TYPES_CHOICES,
    )
    invitation_status = models.CharField(
        max_length=20,
        choices=INVITATION_STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(default=timezone.now)

    