from django import forms
from django.core.exceptions import ValidationError

from .models import (
    Attachment,
    Comment,
    Project,
    SubTask,
    Ticket,
    TrackerGroup,
)


class GroupForm(forms.ModelForm):
    class Meta:
        model = TrackerGroup
        fields = (
            "title",
            "description",
            "members",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "members": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk is None:
            self.fields["members"].initial = (
                [self.initial.get("owner")] if "owner" in self.initial else []
            )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("title", "description")


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = (
            "title",
            "description",
            "priority",
            "ticket_type",
            "due_date",
            "assignee",
        )
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        if project:
            self.fields["assignee"].queryset = project.members.all()


class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ("text", "is_done")
        widgets = {
            "text": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Add task"}
            ),
            "is_done": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


class SecureAttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ["attached_file"]

    def clean_attached_file(self):
        file = self.cleaned_data.get("attached_file")
        if file:
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size must be under 10MB")

            allowed_extensions = ["pdf", "doc", "docx", "jpg", "jpeg", "png"]
            ext = file.name.split(".")[-1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(
                    f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
                )

        return file
