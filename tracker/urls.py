from django.urls import path
from . import views

urlpatterns = [
    path("", view=views.index, name="index"),
    path("groups/list", view=views.group_list, name="group_list"),
    path("groups/create", view=views.create_group, name="create_group"),
    path("groups/<int:group_id>/", views.group_view, name="group_view"),
    path("groups/<int:pk>/delete/", views.group_delete, name="group_delete"),
    path(
        "groups/delete_member/<int:group_id>/<int:pk>",
        view=views.delete_group_member, 
        name="delete_member"
    ),
    path(
        "groups/leave_member/<int:group_id>",
        view=views.leave_group_member,
        name="leave_member"
    ),
    path("invitation/send/<int:group_id>", views.send_invitation, name='send_invitation'),
    #path("members/<int:pk>/profile/", views.view_profile, name="view_profile"),
    #path("members/<int:pk>/delete/", views.delete_member, name="delete_member"),
    path("projects/", view=views.project_list , name="project_list"),
    path("projects/create", view=views.create_project, name="create_project"),
    path("projects/<int:project_id>/", view=views.project_details, name="project_details"),
    path("projects/<int:project_id>/create-ticket", view=views.create_ticket, name="create_ticket"),
    path("tickets/<int:project_id>/", view=views.ticket_detail, name="ticket_detail"),
    path("tickets/<int:project_id>/update", view=views.update_ticket, name="update_ticket"),

    path("api/autocomplete/emails/", view=views.user_email_autocomplete, name="user_email_autocomplete"),
]   