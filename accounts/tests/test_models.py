import pytest
from django.db import IntegrityError
from model_bakery import baker

from accounts.models import TicketsUser


@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self):
        user = baker.make(
            TicketsUser,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )

        assert user.email == "test@example.com"
        assert user.get_full_name() == "John Doe"
        assert user.get_short_name() == "John"
        assert str(user) == "test@example.com"

    def test_user_manager_create_user(self):
        user = TicketsUser.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        assert user.email == "user@example.com"
        assert user.check_password("testpass123")
        assert user.is_active
        assert not user.is_staff

    def test_user_manager_create_superuser(self):
        superuser = TicketsUser.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )

        assert superuser.email == "admin@example.com"
        assert superuser.is_staff
        assert superuser.is_superuser

    def test_user_unique_email(self, db):
        TicketsUser.objects.create_user(
            email="duplicate@example.com", password="testpass123"
        )

        with pytest.raises(IntegrityError):
            TicketsUser.objects.create_user(
                email="duplicate@example.com", password="password123"
            )
