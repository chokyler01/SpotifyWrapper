from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap_data = models.TextField()  # Store wrap info in JSON or text format
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"