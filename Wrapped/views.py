from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import SpotifyWrap
from urllib.parse import urlencode
import requests
from .API_requests import fetch_spotify_data

from django.conf import settings


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
    # Retrieve the access token from session
    access_token = request.session.get('access_token')

    if not access_token:
        # Redirect to Spotify login if token is missing
        return redirect('spotify_login')

    # Spotify API URLs for top tracks and top artists
    top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks'
    top_artists_url = 'https://api.spotify.com/v1/me/top/artists'

    # Fetch top tracks and top artists using the access token from the session
    top_tracks_data = fetch_spotify_data(top_tracks_url, access_token)
    top_artists_data = fetch_spotify_data(top_artists_url, access_token)

    if 'error' in top_tracks_data:
        top_tracks = None
    else:
        top_tracks = top_tracks_data.get('items', [])

    if 'error' in top_artists_data:
        top_artists = None
    else:
        top_artists = top_artists_data.get('items', [])

    # Pass the data to the template
    return render(request, 'wraps.html', {
        'top_tracks': top_tracks,
        'top_artists': top_artists
    })


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
    redirect_uri = 'http://127.0.0.1:8000/callback'
    scopes = ['user-top-read', 'user-follow-read', 'user-read-recently-played', 'streaming']

    auth_url = f"{auth_endpoint}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'scope': ' '.join(scopes), 'response_type': 'code', 'show_dialog': 'true'})}"

    return redirect(auth_url)


def callback(request):
    """ Handle the callback from Spotify and exchange code for access token """
    code = request.GET.get('code')
    if code:
        token_url = 'https://accounts.spotify.com/api/token'
        redirect_uri = 'http://127.0.0.1:8000/callback'
        client_id = 'e1c53cf948ff4cddaa379b88861b2714'
        client_secret = '5d13bd1a4a1c41e193d7546b4b9585b6'

        response = requests.post(token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        })

        token_data = response.json()
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']

        # Save tokens in the session (or store in the database if needed)
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token

        return redirect('view_wraps')



