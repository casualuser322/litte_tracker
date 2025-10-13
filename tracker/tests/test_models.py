import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from model_bakery import baker

from tracker.models import Attachment, Comment, Project, SubTask, Ticket, TrackerGroup


@pytest.mark.django_db
class TestTrackerModels:
    def test_ticket_creation(self, user, project):
        ticket = baker.make(
            Ticket,
            title="Test Ticket",
            project=project,
            creator=user,
            assignee=user,
            status="open",
            priority="high",
        )

        assert ticket.title == "Test Ticket"
        assert ticket.status == "open"
        assert str(ticket) == "Test Ticket (Open)"
        assert ticket.project == project
        assert ticket.creator == user

    def test_ticket_due_date_in_past(self, user, project):
        ticket = Ticket(
            title="Past Due Ticket",
            project=project,
            creator=user,
            due_date=timezone.now() - timezone.timedelta(days=1),
        )

        with pytest.raises(ValidationError):
            ticket.full_clean()

    def test_project_creation_with_group(self, user, group):
        project = baker.make(
            Project, title="Test Project", owner=user, attached_group=group
        )

        assert project.title == "Test Project"
        assert project.attached_group == group
        assert project in group.projects.all()

    def test_comment_creation(self, user, ticket):
        comment = baker.make(Comment, ticket=ticket, author=user, text="Test comment")

        assert comment.text == "Test comment"
        assert comment.author == user
        assert comment in ticket.comments.all()

    def test_attachment_file_validation(self, user, ticket):
        from django.core.files.uploadedfile import SimpleUploadedFile

        invalid_file = SimpleUploadedFile(
            "test.exe", b"file_content", content_type="application/x-msdownload"
        )

        attachment = Attachment(
            ticket=ticket, attached_file=invalid_file, uploaded_by=user
        )

        with pytest.raises(ValidationError):
            attachment.full_clean()

    def test_subtask_completion(self, ticket):
        subtask = baker.make(SubTask, ticket=ticket, text="Test subtask")

        assert not subtask.is_done
        subtask.is_done = True
        subtask.save()

        assert subtask.is_done
        assert "done" in str(subtask)


@pytest.fixture
def user(db):
    from accounts.models import TicketsUser

    return baker.make(TicketsUser, email="test@example.com")


@pytest.fixture
def group(user):
    return baker.make(TrackerGroup, title="Test Group", owner=user)


@pytest.fixture
def project(user, group):
    return baker.make(Project, title="Test Project", owner=user, attached_group=group)


@pytest.fixture
def ticket(user, project):
    return baker.make(
        Ticket, title="Test Ticket", project=project, creator=user, assignee=user
    )
