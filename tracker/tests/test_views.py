import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_bakery import baker


@pytest.mark.django_db
class TestTrackerView:
    def test_group_list_authenticated(self, client, user, group):
        client.force_login(user)
        group.members.add(user)

        response = client.get(reverse('group_list'))

        assert response.status_code == 200
        assert group.title.encode() in response.content

    def test_group_list_unauthenticated(self, client):
        response = client.get(reverse('group_list'))

        assert response.status_code == 302
        assert '/accounts/login' in response.url

    def test_create_group_post(self, client, user):
        client.force_login(user)

        data = {
            'title': 'New Group',
            'description': 'Test description',
            'emails': 'test1@example.com,test2@example.com'
        }

        response = client.post(reverse('create_group'), data)

        assert response.status_code == 302
        assert response.url == reverse('group_list')

    def test_ticket_detail_access(self, client, user, ticket):
        client.force_login(user)
        ticket.project.members.add(user)

        response = client.get(reverse('ticket_detail', kwargs={
            'project_id': ticket.project.id,
            'ticket_id': ticket.id
        }))

        assert response.status_code == 200
        assert ticket.title.encode() in response.content

    def test_ticket_detail_no_access(self, client, user, ticket):
        other_user = baker.make('accounts.TicketsUser', email="other@example.com")
        client.force_login(other_user)

        response = client.get(reverse('ticket_detail', kwargs={
            'project_id': ticket.project.id,
            'ticket_id': ticket.id
        }))

        assert response.status_code == 403

    def test_update_ticket_status_ajax(self, client, user, ticket):
        client.force_login(user)
        ticket.project.members.add(user)

        data = {
            'task_id': ticket.id,
            'status': 'in_progress'
        }

        response = client.post(
            reverse('update_task_status', kwargs={'project_id': ticket.project.id}),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success']
        assert result['status'] == 'in_progress'

    def test_add_comment(self, client, user, ticket):
        client.force_login(user)
        ticket.project.members.add(user)

        data = {
            'text': 'Test comment',
            'add_comment': 'Submit'
        }

        response = client.post(
            reverse('ticket_detail', kwargs={
                'project_id': ticket.project.id,
                'ticket_id': ticket.id
            }),
            data=data
        )

        assert response.status_code == 302
        assert ticket.comments.filter(text='Test comment').exists()

    def test_attachment_upload(self, client, user, ticket):
        client.force_login(user)
        ticket.project.members.add(user)

        test_file = SimpleUploadedFile(
            "test.txt",
            b"file_content",
            content_type="text/plain"
        )

        data = {
            'attached_file': test_file,
            'add_attachment': 'Submit'
        }

        response = client.post(
            reverse('ticket_detail', kwargs={
                'project_id': ticket.project.id,
                'ticket_id': ticket.id
            }),
            data=data
        )

        assert response.status_code == 302
        assert ticket.attachments.count() == 1

    def test_invalid_attachment_upload(self, client, user, ticket):
        client.force_login(user)
        ticket.project.members.add(user)

        invalid_file = SimpleUploadedFile(
            "test.exe",
            b"file_content",
            content_type="application/x-msdownload"
        )

        data = {
            'attached_file': invalid_file,
            'add_attachment': 'Submit'
        }

        response = client.post(
            reverse('ticket_detail', kwargs={
                'project_id': ticket.project.id,
                'ticket_id': ticket.id
            }),
            data=data
        )

        assert response.status_code == 302
        assert ticket.attachments.count() == 0


@pytest.mark.django_db
class TestAPIPermissions:
    def test_user_email_autocomplete(self, client, user):
        client.force_login(user)
        baker.make('accounts.TicketsUser', email="test1@example.com")
        baker.make('accounts.TicketsUser', email="test2@example.com")

        response = client.get(reverse('user_email_autocomplete') + '?q=test')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) == 2

    def test_email_autocomplete_unauthenticated(self, client):
        response = client.get(reverse('user_email_autocomplete') + '?q=test')

        assert response.status_code == 302
