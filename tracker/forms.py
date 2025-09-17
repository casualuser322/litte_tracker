from django import forms 
from .models import Attachment, Comment, Invitation, \
    Project, SubTask, TrackerGroup, Ticket


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
            "title", 
            "description"
        )

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = (
            'title',
            'description',
            'priority',
            'ticket_type',
            'due_data',
        )
        widgets = {
            'due_data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ("text", "is_done")
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control", "placeholder": "Add task"}),
            "is_done": forms.CheckboxInput(attrs={"class": "form-check-input"})
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
