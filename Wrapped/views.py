from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
import requests
from .models import SpotifyWrap
from django.conf import settings
from .API_requests import fetch_spotify_data

def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    """Handle user registration and redirect to Spotify linking."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('spotify_link')  # Redirect to Spotify link after registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """Handle user login."""
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
    """Handle user logout."""
    if request.method == 'POST':
        logout(request)
        return redirect('login')

@login_required
def view_wraps(request):
    """View user's Spotify data after linking their account."""
    try:
        spotify_token = request.session.get('access_token')
        if not spotify_token:
            return redirect('spotify_link')
    except SpotifyWrap.DoesNotExist:
        return redirect('spotify_link')  # Redirect to Spotify link if account not linked

    # Spotify API URLs for top tracks and top artists
    top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks'
    top_artists_url = 'https://api.spotify.com/v1/me/top/artists'

    # Fetch top tracks and top artists using the access token from the session
    top_tracks_data = fetch_spotify_data(top_tracks_url, spotify_token)
    top_artists_data = fetch_spotify_data(top_artists_url, spotify_token)

    # Handle error cases
    top_tracks = top_tracks_data.get('items', []) if 'error' not in top_tracks_data else None
    top_artists = top_artists_data.get('items', []) if 'error' not in top_artists_data else None

    return render(request, 'wraps.html', {'top_tracks': top_tracks, 'top_artists': top_artists})

@login_required
def delete_wrap(request, wrap_id):
    """Allow user to delete their Spotify token (wrap)."""
    wrap = SpotifyWrap.objects.get(id=wrap_id, user=request.user)
    if wrap:
        wrap.delete()
    return redirect('view_wraps')

@login_required
def delete_account(request):
    """Allow user to delete their account."""
    if request.method == 'POST':
        request.user.delete()
        return redirect('register')
    return render(request, 'delete_account.html')

def spotify_login(request):
    """Redirect user to Spotify for authentication."""
    auth_endpoint = "https://accounts.spotify.com/authorize"
    client_id = settings.SPOTIFY_CLIENT_ID
    redirect_uri = settings.SPOTIFY_REDIRECT_URI
    scopes = ['user-top-read', 'user-follow-read', 'user-read-recently-played', 'streaming']

    auth_url = f"{auth_endpoint}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'scope': ' '.join(scopes), 'response_type': 'code'})}"
    return redirect(auth_url)

def callback(request):
    """Handle Spotify callback and store tokens."""
    code = request.GET.get('code')
    if code:
        token_url = 'https://accounts.spotify.com/api/token'
        redirect_uri = settings.SPOTIFY_REDIRECT_URI
        client_id = settings.SPOTIFY_CLIENT_ID
        client_secret = settings.SPOTIFY_CLIENT_SECRET

        response = requests.post(token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        })

        token_data = response.json()
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in')

        # Save tokens in the session (or store in the database if needed)
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token

        return redirect('view_wraps')  # After linking, redirect to view wraps

@login_required
def spotify_link(request):
    """Redirect user to Spotify to link their account."""
    # Redirect to Spotify authentication
    return spotify_login(request)


