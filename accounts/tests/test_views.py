import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestAccountsViews:
    def test_register_view_get(self, client):
        response = client.get(reverse("register"))
        assert response.status_code == 200

    def test_register_view_post(self, client):
        data = {
            "email": "newuser@example.com",
            "username": "newuser123",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpass123",
            "password2": "testpass123",
        }

        response = client.post(reverse("register"), data)

        assert response.status_code == 302

    def test_login_view_get(self, client):
        response = client.get(reverse("signin"))
        assert response.status_code == 200

    def test_login_view_post(self, client, user_with_password):
        data = {
            "email": "test@example.com",
            "password": "testpass123",
        }

        response = client.post(reverse("signin"), data)

        assert response.status_code == 302

    def test_logout_view(self, client, user_with_password):
        client.force_login(user_with_password)
        response = client.get(reverse("logout"))

        assert response.status_code == 302

    def test_profile_view_authenticated(self, client, user_with_password):
        client.force_login(user_with_password)
        response = client.get(reverse("profile"))

        assert response.status_code == 200

    def test_profile_view_unauthenticated(self, client):
        response = client.get(reverse("profile"))
        assert response.status_code == 302

    def test_register_view_post_invalid_form(self, client):
        data = {
            "email": "newuser@example.com",
            "username": "newuser123",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "short",
            "password2": "short",
        }
        response = client.post(reverse("register"), data)

        assert response.status_code == 200
        assert "form" in response.context

    def test_register_view_post_missing_required_fields(self, client):
        data = {
            "email": "newuser@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        response = client.post(reverse("register"), data)

        assert response.status_code == 200
        assert "form" in response.context

    def test_signin_view_post_invalid_credentials(
        self, client, user_with_password
    ):
        data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }
        response = client.post(reverse("signin"), data)

        assert response.status_code == 200
        assert "form" in response.context

    def test_signin_view_post_empty_email(self, client):
        data = {
            "email": "",
            "password": "testpass123",
        }
        response = client.post(reverse("signin"), data)

        assert response.status_code == 200
        assert "form" in response.context

    def test_profile_view_post_update_with_password(
        self, client, user_with_password
    ):
        client.force_login(user_with_password)
        data = {
            "email": "updated@example.com",
            "username": "updateduser",
            "first_name": "Updated",
            "last_name": "User",
            "password": "newpassword123",
        }
        response = client.post(reverse("profile"), data)

        assert response.status_code == 302
        user_with_password.refresh_from_db()

        assert user_with_password.email == "updated@example.com"
        assert user_with_password.check_password("newpassword123")

    def test_profile_view_post_update_without_password(
        self, client, user_with_password
    ):
        client.force_login(user_with_password)

        data = {
            "email": "updated@example.com",
            "username": "updateduser",
            "first_name": "Updated",
            "last_name": "User",
        }
        response = client.post(reverse("profile"), data)

        assert response.status_code == 302
        assert response.url == reverse("profile")

    def test_decline_invitation_success(self, client, user_with_password):
        client.force_login(user_with_password)

        from django.contrib.auth import get_user_model

        from tracker.models import Invitation, TrackerGroup

        User = get_user_model()
        group_owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            first_name="Owner",
            last_name="User",
            password="testpass123",
        )

        group = TrackerGroup.objects.create(
            title="Test Group", owner=group_owner
        )

        invitation = Invitation.objects.create(
            target_user=user_with_password,
            owner=group_owner,
            target_group=group,
            invitation_type="group",
            invitation_status="pending",
        )

        response = client.post(
            reverse("decline_invitation", args=[invitation.id])
        )

        assert response.status_code == 302

        invitation.refresh_from_db()

    def test_accept_invitation_user_already_in_group(
        self, client, user_with_password
    ):
        client.force_login(user_with_password)

        from django.contrib.auth import get_user_model

        from tracker.models import Invitation, TrackerGroup

        User = get_user_model()
        group_owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            first_name="Owner",
            last_name="User",
            password="testpass123",
        )

        group = TrackerGroup.objects.create(
            title="Test Group", owner=group_owner
        )

        group.members.add(user_with_password)

        invitation = Invitation.objects.create(
            target_user=user_with_password,
            owner=group_owner,
            target_group=group,
            invitation_type="group",
            invitation_status="pending",
        )

        response = client.post(
            reverse("accept_invitation", args=[invitation.id])
        )

        assert response.status_code == 302

        assert user_with_password in group.members.all()
