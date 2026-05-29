from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    EXPERIENCE_CHOICES = (
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (2-5 years)'),
        ('senior', 'Senior Level (5+ years)'),
    )
    target_role = models.CharField(max_length=200, blank=True)
    target_company = models.CharField(max_length=200, blank=True)
    experience_level = models.CharField(
        max_length=10,
        choices=EXPERIENCE_CHOICES,
        default='entry'
    )
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    xp_points = models.IntegerField(default=0)
    streak_count = models.IntegerField(default=0)
    last_active = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username