from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("signup/", view=views.register_view, name="signup"),
    path("profile/", view=views.profile_view, name="profile"),
    path("signin/", view=views.signin_view, name="signin"),
    path("login/", view=views.signin_view, name="login"),
    path("logout/", view=views.logout_, name="logout"),
    path("user_<int:pk>", view=views.user_view, name="user_view"),
    path(
        "accept_invitation/<int:inv_id>",
        view=views.accept_invitation,
        name="accept_invitation",
    ),
    path(
        "decline_invitation/<int:inv_id>",
        view=views.decline_invitation,
        name="decline_invitation",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
