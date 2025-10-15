import pytest
from model_bakery import baker

from accounts.models import TicketsUser
from tracker.models import Project, TrackerGroup, Ticket


@pytest.fixture
def user(db):
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
        Ticket,
        title="Test Ticket",
        project=project,
        creator=user,
        assignee=user,
    )

