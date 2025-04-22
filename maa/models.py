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
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    
    def __str__(self):
        return self.username
    
    
from django.db import models
from django.conf import settings

class NutritionEntry(models.Model):
    TIME_SLOTS = [
        ('MORNING',   'Morning'),
        ('NOON',      'Noon'),
        ('EVENING',   'Evening'),
        ('NIGHT',     'Night'),
    ]
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date        = models.DateField()
    time_slot   = models.CharField(max_length=10, choices=TIME_SLOTS)
    description = models.TextField(help_text="What you ate or drank")

    class Meta:
        ordering = ['-date', 'time_slot']

    def __str__(self):
        return f"{self.user.username} – {self.date} {self.time_slot}"
