import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_bakery import baker

from tracker.models import (
    Attachment,
    Comment,
    Project,
    SubTask,
    Ticket,
    TrackerGroup,
)


@pytest.mark.django_db
class TestTrackerView:
    def setup_method(self):
        self.user = baker.make("accounts.TicketsUser", email="test@user.com")
        self.user2 = baker.make("accounts.TicketsUser", email="test2@user.com")
        self.other_user = baker.make(
            "accounts.TicketsUser", email="other@user.com"
        )
        self.group = baker.make("tracker.TrackerGroup", owner=self.user)
        self.group.members.add(self.user)
        self.project = baker.make(
            "tracker.Project", owner=self.user, attached_group=self.group
        )
        self.project.members.add(self.user, self.user2)
        self.ticket = baker.make(
            "tracker.Ticket",
            title="Test Ticket",
            project=self.project,
            creator=self.user,
            assignee=self.user2,
        )
        self.task = SubTask.objects.create(ticket=self.ticket)

    def test_index_authenticated_redirect(self, client):
        client.force_login(self.user)
        response = client.get(reverse("index"))

        assert response.status_code == 302
        assert response.url == reverse("group_list")

    def test_index_unauthenticated_redirect(self, client):
        response = client.get(reverse("index"))

        assert response.status_code == 302
        assert response.url == reverse("register")

    def test_group_list_authenticated(self, client):
        client.force_login(self.user)
        response = client.get(reverse("group_list"))

        assert response.status_code == 200
        assert "owned_groups" in response.context
        assert "member_groups" in response.context

    def test_create_group_get(self, client):
        client.force_login(self.user)
        response = client.get(reverse("create_group"))

        assert response.status_code == 200

    def test_create_group_post_valid(self, client):
        client.force_login(self.user)
        data = {
            "title": "New Group",
            "description": "New Description",
            "emails": "",
        }
        response = client.post(reverse("create_group"), data)

        assert response.status_code == 302
        assert TrackerGroup.objects.filter(title="New Group").exists()

    def test_group_view_with_access(self, client):
        client.force_login(self.user)
        response = client.get(reverse("group_view", args=[self.group.id]))

        assert response.status_code == 200
        assert response.context["group"] == self.group

    def test_project_list(self, client):
        client.force_login(self.user)
        response = client.get(reverse("project_list"))

        assert response.status_code == 200
        assert "projects" in response.context
        assert "owned_projects" in response.context

    def test_create_project_get(self, client):
        client.force_login(self.user)
        response = client.get(reverse("create_project", args=[self.group.id]))

        assert response.status_code == 200

    def test_create_project_post_valid(self, client):
        client.force_login(self.user)
        data = {
            "title": "New Project",
            "description": "New Description",
            "emails": "",
        }
        client.post(reverse("create_project", args=[self.group.id]), data)

        assert Project.objects.filter(title="New Project").exists()

    def test_project_details(self, client):
        client.force_login(self.user)
        response = client.get(
            reverse("project_details", args=[self.project.id])
        )

        assert response.status_code == 200
        assert response.context["project"] == self.project

    def test_ticket_list(self, client):
        client.force_login(self.user2)
        response = client.get(reverse("ticket_list"))

        assert response.status_code == 200
        assert "user_tickets" in response.context

    def test_create_ticket_get(self, client):
        client.force_login(self.user)
        response = client.get(reverse("create_ticket", args=[self.project.id]))

        assert response.status_code == 200

    def test_create_ticket_post_valid(self, client):
        client.force_login(self.user)
        data = {
            "title": "New Ticket",
            "description": "New Description",
            "priority": "medium",
            "ticket_type": "task",
            "assignee": self.user2.id,
        }
        response = client.post(
            reverse("create_ticket", args=[self.project.id]), data
        )

        assert response.status_code == 302
        assert Ticket.objects.filter(title="New Ticket").exists()

    def test_update_ticket_post_valid(self, client):
        client.force_login(self.user)
        data = {
            "title": "Updated Ticket",
            "description": "Updated Description",
            "priority": "high",
            "ticket_type": "bug",
            "assignee": self.user.id,
        }
        response = client.post(
            reverse("update_ticket", args=[self.project.id, self.ticket.id]),
            data,
        )

        assert response.status_code == 302

        self.ticket.refresh_from_db()
        assert self.ticket.title == "Updated Ticket"

    def test_add_subtask_view(self, client):
        client.force_login(self.user)
        data = {"subtask": "New subtask from view"}
        response = client.post(
            reverse("add_subtask", args=[self.ticket.id]), data
        )

        assert response.status_code == 302
        assert SubTask.objects.filter(text="New subtask from view").exists()

    def test_ticket_detail_post_attachment_valid(self, client):
        client.force_login(self.user)

        test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"Test file content",
            content_type="application/pdf",
        )

        data = {"add_attachment": "true", "attached_file": test_file}

        response = client.post(
            reverse("ticket_detail", args=[self.project.id, self.ticket.id]),
            data,
        )

        assert response.status_code in [200, 302]
        if response.status_code == 302:
            assert Attachment.objects.filter(ticket=self.ticket).exists()

    def test_send_invitation_non_owner(self, client):
        group = baker.make("tracker.TrackerGroup", owner=self.other_user)
        client.force_login(self.user)
        data = {"emails": "test@example.com"}
        response = client.post(
            reverse("send_invitation", args=[group.id]), data
        )

        assert response.status_code == 403

    def test_decline_invitation(self, client):
        invitation = baker.make(
            "tracker.Invitation",
            target_user=self.user,
            owner=self.other_user,
            target_group=self.group,
            invitation_type="group",
            invitation_status="pending",
        )

        client.force_login(self.user)
        response = client.post(
            reverse("decline_invitation", args=[invitation.id])
        )

        assert response.status_code == 302
        invitation.refresh_from_db()

    def test_ticket_detail_post_comment(self, client):
        client.force_login(self.user)
        data = {"add_comment": "true", "text": "Test comment"}
        response = client.post(
            reverse("ticket_detail", args=[self.project.id, self.ticket.id]),
            data,
        )

        assert response.status_code == 302
        assert Comment.objects.filter(text="Test comment").exists()

    def test_ticket_detail_post_subtask(self, client):
        client.force_login(self.user)
        data = {"add_subtask": "true", "new_subtask": "Test subtask"}
        response = client.post(
            reverse("ticket_detail", args=[self.project.id, self.ticket.id]),
            data,
        )

        assert response.status_code == 302
        assert SubTask.objects.filter(text="Test subtask").exists()

    def test_user_email_autocomplete(self, client):
        client.force_login(self.user)
        response = client.get(
            reverse("user_email_autocomplete"), {"q": "test"}
        )

        assert response.status_code == 200

        data = json.loads(response.content)
        assert isinstance(data, list)

    def test_update_task_status_valid(self, client):
        client.force_login(self.user)
        data = {"task_id": self.ticket.id, "status": "in_progress"}
        response = client.post(
            reverse("update_task_status", args=[self.project.id]),
            json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200

        self.ticket.refresh_from_db()
        assert self.ticket.status == "in_progress"

    def test_update_task_status_invalid(self, client):
        client.force_login(self.user)
        data = {"task_id": self.ticket.id, "status": "invalid_status"}
        response = client.post(
            reverse("update_task_status", args=[self.project.id]),
            json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_group_delete_as_owner(self, client):
        client.force_login(self.user)
        group_id = self.group.id
        response = client.post(
            reverse("group_delete", args=[self.group.id, self.group.id])
        )

        assert response.status_code == 302
        assert not TrackerGroup.objects.filter(id=group_id).exists()


@pytest.mark.django_db
class TestTrackerEdgeCases:
    def setup_method(self):
        self.user = baker.make("accounts.TicketsUser", email="test@user.com")
        self.other_user = baker.make(
            "accounts.TicketsUser", email="other@user.com"
        )

    def test_access_restricted_views_without_login(self, client):
        urls = [
            reverse("group_list"),
            reverse("create_group"),
            reverse("project_list"),
            reverse("ticket_list"),
        ]

        for url in urls:
            response = client.get(url)
            assert response.status_code in [302, 403]

    def test_nonexistent_objects(self, client):
        client.force_login(self.user)

        response = client.get(reverse("group_view", args=[999]))
        assert response.status_code == 404

        response = client.get(reverse("project_details", args=[999]))
        assert response.status_code == 404

        response = client.get(reverse("ticket_detail", args=[1, 999]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestInvitationViews:
    def setup_method(self):
        self.user = baker.make("accounts.TicketsUser", email="test@user.com")
        self.other_user = baker.make(
            "accounts.TicketsUser", email="other@user.com"
        )
        self.group = baker.make("tracker.TrackerGroup", owner=self.other_user)

    def test_accept_invitation(self, client):
        invitation = baker.make(
            "tracker.Invitation",
            target_user=self.user,
            owner=self.other_user,
            target_group=self.group,
            invitation_type="group",
            invitation_status="pending",
        )

        client.force_login(self.user)
        response = client.post(
            reverse("accept_invitation", args=[invitation.id])
        )

        assert response.status_code == 302
        invitation.refresh_from_db()

        assert invitation.invitation_status == "accepted"
        assert self.user in self.group.members.all()
