from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import SpotifyWrap
from urllib.parse import urlencode



def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('view_wraps')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('view_wraps')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')


@login_required
def view_wraps(request):
    wraps = SpotifyWrap.objects.filter(user=request.user)
    return render(request, 'wraps.html', {'wraps': wraps})


@login_required
def delete_wrap(request, wrap_id):
    wrap = SpotifyWrap.objects.get(id=wrap_id, user=request.user)
    if wrap:
        wrap.delete()
    return redirect('view_wraps')


@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('register')
    return render(request, 'delete_account.html')

def spotify_login(request):
    auth_endpoint = "https://accounts.spotify.com/authorize"
    client_id = 'e1c53cf948ff4cddaa379b88861b2714'
    redirect_uri = 'http://127.0.0.1:8000/'
    scopes = ['user-top-read', 'user-follow-read', 'user-read-recently-played', 'streaming']
    auth_url = f"{auth_endpoint}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'scope': ' '.join(scopes), 'response_type': 'token', 'show_dialog': 'true'})}"
    return redirect(auth_url)