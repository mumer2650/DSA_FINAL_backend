from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # We inherit from AbstractUser so we get username, password, email for free.
    # We can add extra fields here if we want later (e.g., phone_number)
    is_agent = models.BooleanField(default=False) 
    
    def __str__(self):
        return self.username