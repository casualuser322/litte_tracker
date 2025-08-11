from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    members = models.ManyToManyField(User, related_name='projects')

    def __str__(self):
        return self.title

class Group(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_groups"
    )    

    members = models.ManyToManyField(User, related_name="groups")

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
        User,
        on_delete=models.CASCADE,
        related_name='created_tickets',
    )
    assigne = models.ForeignKey(
        User,
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
        User,
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
        User,
        on_delete=models.CASCADE,
    )
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Attachment to {self.ticket.title}"

class TrackerUser():
    pass
# class AuthorisedUser(AbstractUser):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(verbose_name="User email address", unique=True)
#     password = models.
