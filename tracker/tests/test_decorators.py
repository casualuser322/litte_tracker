import pytest
from django.http import HttpRequest

from tracker.decorators import group_access_required, project_access_required


@pytest.mark.django_db
class TestDecorators:
    def test_group_access_required_with_access(self, user, group):
        group.members.add(user)

        @group_access_required
        def test_view(request, group_id, group):
            return "Success"

        request = HttpRequest()
        request.user = user
        response = test_view(request, group_id=group.id)
        assert response == "Success"

    def test_project_access_required_with_access(self, user, project):
        project.members.add(user)

        @project_access_required
        def test_view(request, project_id, project):
            return "Success"

        request = HttpRequest()
        request.user = user
        response = test_view(request, project_id=project.id)
        assert response == "Success"
