import json
from django.db import models
from django.contrib.auth.models import User


class Celebrity(models.Model):
    CATEGORY_CHOICES = [
        ('actor', 'Actor'),
        ('actress', 'Actress'),
        ('singer', 'Singer'),
        ('sports', 'Sports Star'),
        ('influencer', 'Influencer'),
        ('politician', 'Politician'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='celebrities/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='actor')
    description = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = 'Celebrities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class MatchResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_results')
    uploaded_image = models.ImageField(upload_to='uploads/%Y/%m/')
    results_json = models.TextField(default='[]')  # JSON array of {celebrity_id, name, similarity, image_url}
    top_match_name = models.CharField(max_length=200, blank=True, default='')
    top_match_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.top_match_name} ({self.top_match_score:.1f}%)"

    def get_results(self):
        try:
            return json.loads(self.results_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_results(self, results):
        self.results_json = json.dumps(results)
