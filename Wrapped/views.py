from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
import requests
from .models import SpotifyWrap, Profile
from django.conf import settings
from .API_requests import fetch_spotify_data
from django.http import HttpResponse
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.http import FileResponse
import os


@login_required
def generate_wrap_image(request):
   user = request.user
   profile = Profile.objects.get(user=user)


   # Fetch the latest Spotify Wrapped data
   latest_wrap = profile.spotify_wraps.order_by('-created_at').first()
   if not latest_wrap:
       return HttpResponse("No Wrapped data available.", status=404)


   # Initialize wrap data with empty lists
   wrap_data = json.loads(latest_wrap.wrap_data)
   top_tracks = wrap_data.get('top_tracks', [])
   top_artists = wrap_data.get('top_artists', [])
   top_genres = wrap_data.get('top_genres', [])
   top_albums = wrap_data.get('top_albums', [])


   # Helper function to merge data from previous wraps
   def merge_wrap_data(step_wrap):
       if not step_wrap:
           return
       step_data = json.loads(step_wrap.wrap_data)
       nonlocal top_tracks, top_artists, top_genres


       # Safely merge top artists
       step_top_artists = step_data.get('top_artists', [])
       if isinstance(step_top_artists, dict):
           step_top_artists = [step_top_artists]


       if step_top_artists:
           print("Merging Top Artists Data:", json.dumps(step_top_artists, indent=2))
           if not top_artists:
               top_artists = step_top_artists
           else:
               existing_artist_names = {artist['name'] for artist in top_artists}
               new_artists = [artist for artist in step_top_artists if artist['name'] not in existing_artist_names]
               top_artists.extend(new_artists)


   # Check and merge data from previous wraps for the same time range
   if not top_tracks:
       step2_wrap = SpotifyWrap.objects.filter(user=user, time_range=wrap_data['time_range'],
                                               wrap_data__icontains='"step": 2').first()
       merge_wrap_data(step2_wrap)


   if not top_artists or not top_genres:
       step4_wrap = SpotifyWrap.objects.filter(user=user, time_range=wrap_data['time_range'], wrap_data__icontains='"top_artists"').first()
       print("Step 4 Wrap Found:", step4_wrap is not None)
       merge_wrap_data(step4_wrap)


   # Debug: Print after merging
   print("Merged Top Artists Data:", top_artists)


   # Create a blank image using Pillow
   img = Image.new('RGB', (800, 600), color='white')
   draw = ImageDraw.Draw(img)


   # Define font (using a basic system font)
   font_path = "/Library/Fonts/Arial.ttf"
   font = ImageFont.truetype(font_path, 20)


   # Add text content to the image
   draw.text((20, 20), f"Spotify Wrapped Summary for {user.username}", fill="black", font=font)


   y_offset = 60


   # Display Top Tracks
   draw.text((20, y_offset), "Top Tracks:", fill="black", font=font)
   y_offset += 30
   if top_tracks:
       for i, track in enumerate(top_tracks[:5]):  # Limit to top 5 tracks for space
           track_name = track.get('name', 'Unknown Track')
           artists = ", ".join(track.get('artists', ['Unknown Artist']))
           draw.text((40, y_offset), f"{i + 1}. {track_name} by {artists}", fill="black", font=font)
           y_offset += 30
   else:
       draw.text((40, y_offset), "No tracks available", fill="black", font=font)
       y_offset += 30


   # Display Top Artists
   draw.text((20, y_offset), "Top Artists:", fill="black", font=font)
   y_offset += 30
   if top_artists:
       for i, artist in enumerate(top_artists[:5]):
           artist_name = artist.get('name', 'Unknown Artist')
           draw.text((40, y_offset), f"{i + 1}. {artist_name}", fill="black", font=font)
           y_offset += 30
   else:
       draw.text((40, y_offset), "No artists available", fill="black", font=font)
       y_offset += 30


   # Display Top Albums
   draw.text((20, y_offset), "Top Albums:", fill="black", font=font)
   y_offset += 30
   if top_albums:
       for i, album in enumerate(top_albums[:5]):
           album_name = album.get('name', 'Unknown Album')
           artists = ", ".join(album.get('artists', ['Unknown Artist']))
           draw.text((40, y_offset), f"{i + 1}. {album_name} by {artists}", fill="black", font=font)
           y_offset += 30
   else:
       draw.text((40, y_offset), "No albums available", fill="black", font=font)


   print("Aggregated Top Tracks:", top_tracks)
   print("Aggregated Top Artists:", top_artists)
   print("Aggregated Top Albums:", top_albums)


   # Save image to an in-memory file
   image_io = BytesIO()
   img.save(image_io, format='PNG')
   image_io.seek(0)


   # Return the image as a response
   return FileResponse(image_io, as_attachment=True, filename='spotify_wrapped.png')


@login_required
def choose_wrap_time(request):
  if request.method == 'POST':
      # Get the selected time range from the form
      time_range = request.POST.get('time_range')
      print("Selected Time Range:", time_range)  # Debugging
      request.session['time_range'] = time_range




      # Validate the selected time range
      valid_time_ranges = ['short_term', 'medium_term', 'long_term']
      if time_range not in valid_time_ranges:
          time_range = 'medium_term'  # Fallback to 'medium_term' if invalid




      # Redirect to the view wraps page with the selected time range
      return redirect(f'/wraps/?time_range={time_range}')




  return render(request, 'choose_time.html')




@login_required
def profile_view(request):
 user = request.user
 profile = Profile.objects.get(user=user)








 short_term_wraps = profile.spotify_wraps.filter(time_range='short_term').order_by('-created_at')
 medium_term_wraps = profile.spotify_wraps.filter(time_range='medium_term').order_by('-created_at')
 long_term_wraps = profile.spotify_wraps.filter(time_range='long_term').order_by('-created_at')








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
         Profile.objects.create(user=user)  # Create profile for new user
         login(request, user)  # Log in the user immediately after registration
         return redirect('login')  # Redirect to choose_wrap_time after login
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
         return redirect('spotify_login')
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
















# views.py
from datetime import datetime

def view_wraps(request):
    """Sequential view for user's Spotify data (top songs, top albums, top artists) with different time ranges."""
    spotify_token = request.session.get('access_token')
    if not spotify_token:
        return redirect('spotify_link')

    step = int(request.GET.get('step', 1))
    time_range = request.GET.get('time_range')
    valid_time_ranges = ['short_term', 'medium_term', 'long_term']

    if time_range not in valid_time_ranges:
        time_range = request.session.get('time_range', 'medium_term')

    params = {'limit': 10, 'time_range': time_range}
    today_date = datetime.today().date()

    wrap = SpotifyWrap.objects.create(
        user=request.user,
        time_range=time_range,
        wrap_data=json.dumps({})
    )

    # Load existing wrap data
    wrap_data = json.loads(wrap.wrap_data)

    # Ensure `time_range` is included in wrap_data
    wrap_data['time_range'] = time_range

    # Step 2: Fetch Top Tracks
    if step == 2:
        top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks'
        top_tracks_data = fetch_spotify_data(top_tracks_url, spotify_token, params=params)
        top_tracks = [
            {
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
            }
            for track in top_tracks_data.get('items', [])
        ]
        wrap_data['top_tracks'] = top_tracks

        # Save the wrap data
        wrap.wrap_data = json.dumps(wrap_data)
        wrap.save()

        # Save the wrap to the user's profile
        save_wrap_to_profile(request.user, wrap, time_range)

    # Step 4: Fetch Top Artists
    elif step == 4:
        top_artists_url = 'https://api.spotify.com/v1/me/top/artists'
        top_artists_data = fetch_spotify_data(top_artists_url, spotify_token, params=params)
        top_artists = [
            {
                'name': artist.get('name', 'Unknown Artist'),
                'genres': artist.get('genres', []),
                'image_url': artist['images'][0]['url'] if artist.get('images') else None
            }
            for artist in top_artists_data.get('items', [])
        ]

        wrap_data['top_artists'] = top_artists

        # Ensure `time_range` is included in wrap_data
        wrap_data['time_range'] = time_range

        # Save the wrap data
        wrap.wrap_data = json.dumps(wrap_data)
        wrap.save()

        # Save the wrap to the user's profile
        save_wrap_to_profile(request.user, wrap, time_range)

    # Step 6: Fetch Top Albums
    elif step == 6:
        top_artists_url = 'https://api.spotify.com/v1/me/top/artists'
        top_artists_data = fetch_spotify_data(top_artists_url, spotify_token, params=params)
        top_albums = []
        for artist in top_artists_data.get('items', []):
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

        wrap_data['top_albums'] = top_albums[:10]

        # Ensure `time_range` is included in wrap_data
        wrap_data['time_range'] = time_range

        # Save the wrap data
        wrap.wrap_data = json.dumps(wrap_data)
        wrap.save()

        if not request.session.get(f'saved_{time_range}', False):
            save_wrap_to_profile(request.user, wrap, time_range)
            # Mark as saved in session
            request.session[f'saved_{time_range}'] = True


        # Save the wrap to the user's profile
        save_wrap_to_profile(request.user, wrap, time_range)

    # Render the wraps page with the collected data
    return render(request, 'wraps.html', {
        'step': step,
        'time_range': time_range,
        'top_tracks': wrap_data.get('top_tracks', []),
        'top_artists': wrap_data.get('top_artists', []),
        'top_genres': wrap_data.get('top_genres', []),
        'top_albums': wrap_data.get('top_albums', []),
    })



@login_required
def delete_account(request):
 """Allow user to delete their account."""
 if request.method == 'POST':
     request.user.delete()
     return redirect('register')
 return render(request, 'delete_account.html')












@login_required
def spotify_login(request):
 """Redirect user to Spotify for authentication."""
 auth_endpoint = "https://accounts.spotify.com/authorize"
 client_id = settings.SPOTIFY_CLIENT_ID
 redirect_uri = settings.SPOTIFY_REDIRECT_URI
 scopes = ['user-top-read', 'user-follow-read', 'user-read-recently-played', 'streaming']








 # Add `show_dialog=true` to force re-authentication
 auth_url = f"{auth_endpoint}?{urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'scope': ' '.join(scopes), 'response_type': 'code', 'show_dialog': 'true'})}"
 return redirect(auth_url)








import json
















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








     return redirect('choose_wrap_time')  # After linking, redirect to view wraps








 return HttpResponse("No authorization code provided.", status=400)
















def spotify_link(request):
 """Redirect user to Spotify to link their account."""
 # Redirect to Spotify authentication
 return spotify_login(request)








def save_wrap_to_profile(user, wrap, time_range):
    """Save a wrap to the user's profile if it's not already saved for the specific time range."""
    profile, created = Profile.objects.get_or_create(user=user)

    # Check if a wrap with the same time range exists in the user's profile
    if not profile.spotify_wraps.filter(id=wrap.id, time_range=time_range).exists():
        profile.spotify_wraps.add(wrap)
        print(f"Wrap {wrap.id} added to profile for user {user.username} and time range {time_range}.")
    else:
        print(f"Wrap {wrap.id} already exists in profile for user {user.username} and time range {time_range}. Skipping save.")




def view_old_wrap(request, wrap_id):
  """View for displaying details of a specific wrap based on wrap_id."""




  # Retrieve the wrap object by wrap_id (ensure it's the current user)
  wrap = get_object_or_404(SpotifyWrap, id=wrap_id, user=request.user)




  # Load the wrap data from the database (assuming it's stored as JSON)
  wrap_data = json.loads(wrap.wrap_data)




  # Extract the necessary data from wrap_data
  step = wrap_data.get('step')
  time_range = wrap_data.get('time_range')
  top_tracks = wrap_data.get('top_tracks', [])
  top_artists = wrap_data.get('top_artists', [])
  top_genres = wrap_data.get('top_genres', [])
  top_albums = wrap_data.get('top_albums', [])




  # Render the wrap details in a template
  return render(request, 'view_old_wrap.html', {
      'wrap_id': wrap.id,
      'step': step,
      'time_range': time_range,
      'top_tracks': top_tracks,
      'top_artists': top_artists,
      'top_genres': top_genres,
      'top_albums': top_albums,
  })
