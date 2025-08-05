from django.db import models
from django.contrib.auth.models import User


class TicketsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    
    profile_image = models.ImageField(upload_to='user_avatars/')


    def __str__(self):
        return self.user.username