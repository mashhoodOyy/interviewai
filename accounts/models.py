from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import date, timedelta

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

    def update_streak(self):
        today = date.today()

        if self.last_active is None:
            # first time ever
            self.streak_count = 1
            self.last_active = today

        elif self.last_active == today:
            # already practiced today — no change
            pass

        elif self.last_active == today - timedelta(days=1):
            # practiced yesterday — increment streak
            self.streak_count += 1
            self.last_active = today

        else:
            # missed a day — reset streak
            self.streak_count = 1
            self.last_active = today

        self.save()