from django.urls import path
from . import views

urlpatterns = [
    path("", view=views.index, name="index"),
    path("projects/", view=views.project_list , name="project_list"),
    path("projects/create", view=views.create_project, name="create_project"),
    path("projects/<int:project_id>/", view=views.project_details, name="project_details"),
    path("projects/<int:project_id>/create-ticket", view=views.create_ticket, name="create_ticket"),
    path("tickets/<int:project_id>/", view=views.ticket_detail, name="ticket_detail"),
    path("tickets/<int:project_id>/update", view=views.update_ticket, name="update_ticket"),
]   