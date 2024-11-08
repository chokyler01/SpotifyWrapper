from django.db import models
from django.contrib.auth.models import User

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap_data = models.TextField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    time_range = models.CharField(max_length=20, choices=[
        ('short_term', 'Short Term'),
        ('medium_term', 'Medium Term'),
        ('long_term', 'Long Term')
    ])
    public = models.BooleanField(default=False)  # Ensure this field is defined

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

class Friendship(models.Model):
    user = models.ForeignKey(User, related_name='friendships', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"
