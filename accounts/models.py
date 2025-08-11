from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser, PermissionsMixin

from tracker.models import Ticket, Project, Group


class TicketsUser(AbstractUser, PermissionsMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=150)
    date_joined = models.DateTimeField(default=timezone.now)
    email = models.EmailField(verbose_name='User email address', unique=True)

    profile_image = models.ImageField(upload_to='user_avatars/')

    # TODO password + hash

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = ['email']
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.user.username()

class TicketUserEngine(models.Model):
    """
    This class is created for validation and managing new users
    """
    def create_user():
        ...

    def create_superuser():
        ...
    
