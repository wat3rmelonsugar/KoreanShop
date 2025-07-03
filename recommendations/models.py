# models.py
from django.db import models
from django.contrib.auth import get_user_model


class UserRecommendation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    recommendation_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']