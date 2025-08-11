from django.db import models
from django.utils import timezone
from django.contrib.auth.models import \
    User, AbstractUser, PermissionsMixin, BaseUserManager

from tracker.models import Ticket, Project, Group


class TicketUserEngine(BaseUserManager):
    """
    This class is created for validation and managing new users
    """
    def create_user(
            self,
            email,
            password=None,
            **extra_fields
        ):
        if not email:
            raise ValueError("Email is requierd")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_superuser(
            self,
            email,
            password=None,
            **extra_fields
        ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staf=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        
        return self.create_user(email, password, **extra_fields)
        

class TicketsUser(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=150)
    date_joined = models.DateTimeField(default=timezone.now)

    profile_image = models.ImageField(
        upload_to='user_avatars/',
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = TicketUserEngine()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.user.username()