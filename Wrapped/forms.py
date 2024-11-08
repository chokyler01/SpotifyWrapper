from django import forms
from django.contrib.auth.models import User

class AddFriendForm(forms.Form):
    friend_username = forms.CharField(label="Friend's Username", max_length=150)

    def clean_friend_username(self):
        username = self.cleaned_data['friend_username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this username does not exist.")
        return username
