from django.contrib.auth.backends import ModelBackend

from .models import TicketsUser


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = TicketsUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except TicketsUser.DoesNotExist:
            return None


AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]
