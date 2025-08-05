from django import forms 
from .models import Attachment, Comment, Project, Ticket


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'members',
        ]

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'title',
            'description',
            'status',
            'priority',
            'ticket_type',
            'due_data',
            'assigne',
        ]
        widgets = {
            'due_data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3})
        }

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['attached_file']
