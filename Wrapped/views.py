from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
import requests
from .models import SpotifyWrap
from django.conf import settings
from .API_requests import fetch_spotify_data
from django.http import HttpResponse
from collections import Counter



def choose_wrap_time(request):
    """Allow user to select the time range for their Spotify Wrapped."""
    return render(request, 'choose_time.html')

@login_required()
def profile_view(request):
    user = request.user
    # Retrieve wraps for each time range and order them by date
    short_term_wraps = SpotifyWrap.objects.filter(user=user, time_range='short_term').order_by('-created_at')
    medium_term_wraps = SpotifyWrap.objects.filter(user=user, time_range='medium_term').order_by('-created_at')
    long_term_wraps = SpotifyWrap.objects.filter(user=user, time_range='long_term').order_by('-created_at')

    # Add the wraps to the context with labels for each term
    context = {
        'user': user,
        'short_term_wraps': short_term_wraps,
        'medium_term_wraps': medium_term_wraps,
        'long_term_wraps': long_term_wraps,
    }
    return render(request, 'profile.html', context)

def contact_view(request):
    """Display the Contact Developers page."""
    return render(request, 'contact.html')

def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    """Handle user registration and redirect to Spotify linking."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return spotify_login(request)  # Redirect to Spotify authorization
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
            return redirect('choose_wrap_time')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Handle user logout and clear Spotify session data."""
    if request.method == 'POST':
        # Clear Spotify session data if it exists
        request.session.pop('access_token', None)
        request.session.pop('refresh_token', None)
        logout(request)
    return redirect('login')

def view_wraps(request):
    """Display user's Spotify data (top songs, top albums, top artists) with selected time range."""
    spotify_token = request.session.get('access_token')
    if not spotify_token:
        return redirect('spotify_link')

    # Ensure time_range is provided; otherwise, redirect to choose time
    time_range = request.GET.get('time_range')
    if not time_range:
        return redirect('choose_wrap_time')

    print(f"Selected Time Range: {time_range}")  # Debugging line

    # Get the current step (default to step 1)
    step = int(request.GET.get('step', 1))

    # Spotify API URLs
    top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks'
    top_artists_url = 'https://api.spotify.com/v1/me/top/artists'

    # Initialize data variables
    top_tracks, top_artists, top_genres, top_albums = [], [], [], []

    # Retrieve and display data based on the current step
    if step == 1:
        # Fetch top tracks for the selected time range
        top_tracks_data = fetch_spotify_data(top_tracks_url, spotify_token, params={'limit': 10, 'time_range': time_range})
        top_tracks = [
            {
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album_name': track['album']['name'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
            }
            for track in top_tracks_data.get('items', [])
        ]
        wrap_data = {'step': step, 'top_tracks': top_tracks, 'time_range': time_range}
        SpotifyWrap.objects.create(user=request.user, wrap_data=json.dumps(wrap_data), time_range=time_range)

    elif step == 2:
        # Fetch top artists and genres for the selected time range
        top_artists_data = fetch_spotify_data(top_artists_url, spotify_token, params={'limit': 10, 'time_range': time_range})
        top_artists = [
            {
                'name': artist['name'],
                'genres': artist.get('genres', []),
                'image_url': artist['images'][0]['url'] if artist.get('images') else None
            }
            for artist in top_artists_data.get('items', [])
        ]
        genres = [genre for artist in top_artists for genre in artist['genres']]
        genre_counts = Counter(genres)
        top_genres = genre_counts.most_common(5)
        wrap_data = {'step': step, 'top_artists': top_artists, 'top_genres': top_genres, 'time_range': time_range}
        SpotifyWrap.objects.create(user=request.user, wrap_data=json.dumps(wrap_data), time_range=time_range)

    elif step == 3:
        # Fetch top albums for each top artist for the selected time range
        top_artists_data = fetch_spotify_data(top_artists_url, spotify_token, params={'limit': 10, 'time_range': time_range})
        top_artists = top_artists_data.get('items', []) if 'error' not in top_artists_data else []
        for artist in top_artists:
            artist_albums_url = f'https://api.spotify.com/v1/artists/{artist["id"]}/albums'
            albums_data = fetch_spotify_data(artist_albums_url, spotify_token, params={'limit': 3})
            albums = [
                {
                    'name': album['name'],
                    'artists': [artist['name'] for artist in album['artists']],
                    'image_url': album['images'][0]['url'] if album['images'] else None
                }
                for album in albums_data.get('items', [])
            ]
            top_albums.extend(albums)
        wrap_data = {'step': step, 'top_albums': top_albums, 'time_range': time_range}
        SpotifyWrap.objects.create(user=request.user, wrap_data=json.dumps(wrap_data), time_range=time_range)

    return render(request, 'wraps.html', {
        'step': step,
        'top_tracks': top_tracks,
        'top_artists': top_artists,
        'top_genres': top_genres,
        'top_albums': top_albums,
        'time_range': time_range
    })


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

    # Add `show_dialog=true` to force re-authentication
    auth_url = f"{auth_endpoint}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'scope': ' '.join(scopes), 'response_type': 'code', 'show_dialog': 'true'})}"
    return redirect(auth_url)

import json  # Import json for pretty printing (optional)


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

        if response.status_code != 200:
            print("Error obtaining access token: ", response.status_code)
            print("Response Text: ", response.text)
            return HttpResponse("An error occurred while retrieving the access token. Please try again.", status=500)

        token_data = response.json()

        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in')

        # Debugging: print token data
        print("Access Token:", access_token)
        print("Refresh Token:", refresh_token)

        user_profile_url = 'https://api.spotify.com/v1/me'
        profile_response = requests.get(user_profile_url, headers={
            'Authorization': f'Bearer {access_token}'
        })

        # Debugging: print profile response status code and text
        print("Profile Response Status Code:", profile_response.status_code)
        print("Profile Response Text:", profile_response.text)

        if profile_response.status_code != 200:
            print("Error fetching user profile: ", profile_response.status_code)
            print("Response Text: ", profile_response.text)
            return HttpResponse("An error occurred while fetching user profile data. Please try again.", status=500)

        profile_data = profile_response.json()
        print("User Profile Data:", json.dumps(profile_data, indent=2))

        if 'error' in token_data:
            print("Error in token response:", token_data['error'])
            return HttpResponse("An error occurred with the token data. Please try again.", status=500)

        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token

        return redirect('view_wraps')  # After linking, redirect to view wraps

    return HttpResponse("No authorization code provided.", status=400)


def spotify_link(request):
    """Redirect user to Spotify to link their account."""
    # Redirect to Spotify authentication
    return spotify_login(request)
