from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    # path('register/', views.register, name='register'),
    path('signup/', view=views.register_view, name='register'),
    path('profile/', view=views.profile_view, name='profile'),
    path('signin/', view=views.signin_view, name='signin'),
    path('login/', view=views.signin_view, name='login'),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)