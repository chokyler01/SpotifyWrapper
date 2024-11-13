from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   spotify_wraps = models.ManyToManyField('SpotifyWrap', blank=True, related_name='profiles')


   def __str__(self):
       return f"Profile of {self.user.username}"


class SpotifyWrap(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   wrap_data = models.TextField(default=dict)
   created_at = models.DateTimeField(auto_now_add=True)
   time_range = models.CharField(
       max_length=20,
       choices=[
           ('short_term', 'Short Term'),
           ('medium_term', 'Medium Term'),
           ('long_term', 'Long Term')
       ],
   )


   def __str__(self):
       return f"{self.user.username} - {self.created_at}"