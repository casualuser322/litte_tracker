from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.index, name="index"),
    path("groups/list", view=views.group_list, name="group_list"),
    path("groups/create", view=views.create_group, name="create_group"),
    path("groups/<int:group_id>/", views.group_view, name="group_view"),
    path(
        "groups/<int:group_id>/<int:pk>/delete/",
        views.group_delete,
        name="group_delete",
    ),
    path(
        "groups/<int:group_id>/edit",
        view=views.edit_group,
        name="edit_group",
    ),
    path(
        "groups/delete_member/<int:group_id>/<int:pk>",
        view=views.delete_group_member,
        name="delete_member",
    ),
    path(
        "groups/leave_member/<int:group_id>",
        view=views.leave_group_member,
        name="leave_member",
    ),
    path(
        "invitation/send/<int:group_id>",
        views.send_invitation,
        name="send_invitation",
    ),
    path("projects/", view=views.project_list, name="project_list"),
    path(
        "projects/edit/<int:project_id>",
        views.edit_project,
        name="edit_project",
    ),
    path(
        "projects/delete/<int:group_id>/<int:project_id>",
        views.delete_project,
        name="delete_project",
    ),
    path(
        "projects/create/<int:group_id>/",
        views.create_project,
        name="create_project",
    ),
    path(
        "projects/<int:project_id>/",
        view=views.project_details,
        name="project_details",
    ),
    path(
        "projects/<int:project_id>/create-ticket",
        view=views.create_ticket,
        name="create_ticket",
    ),
    path("tickets/list", view=views.ticket_list, name="ticket_list"),
    path(
        "tickets/<int:project_id>/<int:ticket_id>/",
        view=views.ticket_detail,
        name="ticket_detail",
    ),
    path(
        "tickets/<int:project_id>/update",
        view=views.update_ticket,
        name="update_ticket",
    ),
    path(
        "tickets/<int:ticket_id>/add_subtask/",
        view=views.add_subtask,
        name="add_subtask",
    ),
    path(
        "tickets/<int:ticket_id>/update_status/<int:pk>/",
        views.update_task_ajax,
        name="update_task_ajax",
    ),
    path(
        "tickets/update_task_status/<int:project_id>",
        view=views.update_task_status,
        name="update_task_status",
    ),
    path(
        "api/autocomplete/emails/",
        view=views.user_email_autocomplete,
        name="user_email_autocomplete",
    ),
]
