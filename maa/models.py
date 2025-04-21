from django.db import models
from django.contrib.auth.models import AbstractUser

class WomanUser(AbstractUser):
    GENDER_CHOICES = [
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='F')
    phone_number = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.username