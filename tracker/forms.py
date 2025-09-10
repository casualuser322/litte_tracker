from django import forms 
from .models import Attachment, Comment, Invitation, TrackerGroup, Project, Ticket


class GroupForm(forms.ModelForm):
    class Meta:
        model = TrackerGroup
        fields = (
            'title',
            'description',
            'members',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'members': forms.CheckboxSelectMultiple(),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'title',
            'description',
            'owner',
            'members',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'members': forms.CheckboxSelectMultiple
        }

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = (
            'title',
            'description',
            'status',
            'priority',
            'ticket_type',
            'due_data',
            'assigne',
        )
        widgets = {
            'due_data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3})
        }

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ('attached_file',)

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = (
            'target_user',
            'invitation_type',
        )