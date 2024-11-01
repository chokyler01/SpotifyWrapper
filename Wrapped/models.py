from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

from django.utils import timezone

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap_data = models.TextField(default=dict)  # Store wrap info in JSON or text format
    wrap_date = models.DateField(default=timezone.now)  # Add this line for wrap_date
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
