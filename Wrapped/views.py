from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import SpotifyWrap
from .spotify_token import fetch_spotify_data  # Import the token and data fetching logic

def test_spotify_view(request):
    top_artists_endpoint = "https://api.spotify.com/v1/me/top/artists?limit=5"
    
    # Fetch top artists from Spotify
    top_artists = fetch_spotify_data(top_artists_endpoint)
    
    return JsonResponse(top_artists)

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
@login_required
def view_wraps(request):
    # Spotify API endpoint for top artists and tracks
    top_artists_endpoint = "https://api.spotify.com/v1/me/top/artists?limit=5"
    top_tracks_endpoint = "https://api.spotify.com/v1/me/top/tracks?limit=5"

    # Fetch Spotify data
    top_artists = fetch_spotify_data(top_artists_endpoint)
    top_tracks = fetch_spotify_data(top_tracks_endpoint)

    # Check for errors
    if 'error' in top_artists:
        artists = []  # Fallback to empty list if there’s an error
    else:
        artists = [{'name': artist['name'], 'image_url': artist['images'][0]['url']} for artist in top_artists.get('items', [])]

    if 'error' in top_tracks:
        songs = []  # Fallback to empty list if there’s an error
    else:
        songs = [{'title': track['name'], 'artist_name': track['artists'][0]['name']} for track in top_tracks.get('items', [])]

    # Fetch user wraps from the database
    wraps = SpotifyWrap.objects.filter(user=request.user)

    # Send data to the template
    context = {
        'wraps': wraps,
        'artists': artists,
        'songs': songs
    }

    return render(request, 'wraps.html', context)


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
