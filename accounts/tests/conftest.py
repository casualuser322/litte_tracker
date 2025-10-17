import pytest
from model_bakery import baker

from accounts.models import TicketsUser


@pytest.fixture
def user(db):
    return baker.make(TicketsUser, email="test@example.com")


@pytest.fixture
def user_with_password(db):
    user = baker.make(
        TicketsUser, email="test@example.com", username="testuser"
    )
    user.set_password("testpass123")
    user.save()
    return user
