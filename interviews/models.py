from django.db import models
from django.conf import settings

class InterviewSession(models.Model):
    MODE_CHOICES = (
        ('quick', 'Quick Practice'),
        ('full', 'Full Interview'),
        ('custom', 'Custom'),
    )
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    overall_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_title}"

    class Meta:
        ordering = ['-created_at']

class Question(models.Model):
    CATEGORY_CHOICES = (
        ('behavioral', 'Behavioral'),
        ('technical', 'Technical'),
        ('situational', 'Situational'),
        ('culture_fit', 'Culture Fit'),
    )
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"

    class Meta:
        ordering = ['order']

class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    text = models.TextField()
    ai_score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    improvement_tips = models.TextField(blank=True)
    ideal_answer = models.TextField(blank=True)
    filler_word_count = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to Q{self.question.order}"

class Badge(models.Model):
    BADGE_CHOICES = (
        ('first_interview', '🎯 First Interview'),
        ('streak_7', '🔥 7 Day Streak'),
        ('perfect_score', '⭐ Perfect Score'),
        ('speed_demon', '⚡ Speed Demon'),
        ('expert', '🏆 Expert'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    name = models.CharField(max_length=20, choices=BADGE_CHOICES)
    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        unique_together = ['user', 'name']