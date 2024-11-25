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
from django.utils.translation import get_language
from django.utils.translation import activate  # Import activate for language switching
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

@login_required
def view_friends_old_wrap(request, friend_id):
    """View to display a friend's old wraps."""
    friend_user = get_object_or_404(User, id=friend_id)
    if not friend_user.profile in request.user.profile.friends.all():
        return HttpResponse("You are not friends with this user.", status=403)

    wraps = SpotifyWrap.objects.filter(user=friend_user).order_by('-created_at')

    return render(request, 'view_friends_old_wrap.html', {
        'friend': friend_user,
        'wraps': wraps,
    })


@login_required
def friends_page(request):
    profile = request.user.profile
    friends = profile.friends.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        action = request.POST.get('action')

        if username:
            try:
                friend_user = User.objects.get(username=username)
                friend_profile = friend_user.profile

                if action == 'add':
                    if friend_profile not in profile.friends.all():
                        profile.friends.add(friend_profile)
                        messages.success(request, f"You are now friends with {username}!")
                    else:
                        messages.info(request, f"{username} is already your friend.")
                elif action == 'remove':
                    if friend_profile in profile.friends.all():
                        profile.friends.remove(friend_profile)
                        messages.success(request, f"You have removed {username} as a friend.")
                    else:
                        messages.info(request, f"{username} is not your friend.")
            except User.DoesNotExist:
                messages.error(request, f"User with username {username} does not exist.")

    return render(request, 'friends_page.html', {'friends': friends})


@login_required
def logout_view(request):
    """Handle user logout and redirect to login page."""
    if request.method == 'POST':
        logout(request)
        return redirect('login')


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

    language_code = request.session.get('language')
    activate(language_code)  # Activate the selected language



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




  # Get the current step (default to 1, which shows top songs)
  step = int(request.GET.get('step', 1))
  time_range = request.GET.get('time_range')


  # Define the valid time ranges directly
  valid_time_ranges = ['short_term', 'medium_term', 'long_term']


  # Check if the time_range is valid; if not, redirect to choose_wrap_time
  if time_range not in valid_time_ranges:
      print("Invalid time_range detected:", time_range)
      time_range = request.session.get('time_range')


  # Use the selected time range directly
  time_range_param = time_range
  print(f"Time Range in view_wraps: {time_range_param}")


  # Your existing code to fetch data using time_range_param
  # For example:
  params = {'limit': 10, 'time_range': time_range_param}


  # Spotify API URLs
  top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks'
  top_artists_url = 'https://api.spotify.com/v1/me/top/artists'
  top_albums_url = 'https://api.spotify.com/v1/me/top/albums'




  # Initialize data variables
  top_tracks, top_artists, top_genres, top_albums = [], [], [], []




  # Define the parameters to pass to Spotify API based on the time range
  params = {'limit': 10, 'time_range': time_range_param}

  headers = {
      'Authorization': f'Bearer {spotify_token}',
  }


  # Check if a wrap already exists for the user for this time range and today
  today_date = datetime.today().date()
  # Check if any wrap already exists for the user for today
  existing_wrap = SpotifyWrap.objects.filter(
      user=request.user,
      created_at__date=today_date,
      time_range=time_range_param
  ).first()


  if existing_wrap:
      # If a wrap exists, check if the time range matches the selected one
      if existing_wrap.time_range != time_range_param:
          # Create a new wrap for the selected time range
          wrap = SpotifyWrap.objects.create(
              user=request.user,
              time_range=time_range_param,
              wrap_data=json.dumps({})
          )
      else:
          # Update the existing wrap
          wrap = existing_wrap
  else:
      # No wrap exists, create a new one
      wrap = SpotifyWrap.objects.create(
          user=request.user,
          time_range=time_range_param,
          wrap_data=json.dumps({})
      )
  creation_month_day = str(wrap.created_at)[5:10]




  # Retrieve and save data based on the current step
  if step == 2:
      # Fetch top tracks with album images
      print(f"Requesting top tracks from URL: {top_tracks_url} with params: {params}")
      #
      #
      # top_tracks_data = fetch_spotify_data(top_tracks_url, spotify_token, params=params)
      # top_tracks = [
      #     {
      #         'name': track['name'],
      #         'artists': [artist['name'] for artist in track['artists']],
      #         'album_name': track['album']['name'],
      #         'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
      #     }
      #     for track in top_tracks_data.get('items', [])
      # ]
      songs_url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_range}'
      top_tracks_data = requests.get(songs_url, headers=headers)
      top_tracks = (top_tracks_data.json().get('items', []))[0:10]

      for track in top_tracks:
          if track.get('album') and track['album'].get('images'):
              track['album_image'] = track['album']['images'][0]['url']
          else:
              track['album_image'] = None







              # Save or update wrap data with top tracks
      wrap_data = {
          'step': step,
          'time_range': time_range_param,
          'top_tracks': top_tracks,
      }
      if wrap:
          # Update existing wrap data
          wrap.wrap_data = json.dumps(wrap_data)
          wrap.save()
      else:
          # Create new wrap for today
          wrap = SpotifyWrap.objects.create(user=request.user, wrap_data=json.dumps(wrap_data), time_range=time_range_param)




  elif step == 4:
      # Fetch top artists with images and genres
      top_artists_data = fetch_spotify_data(top_artists_url, spotify_token, params=params)
      top_artists = [
          {
              'name': artist['name'],
              'genres': artist.get('genres', []),
              'image_url': artist['images'][0]['url'] if artist.get('images') else None
          }
          for artist in top_artists_data.get('items', [])
      ]




      # Aggregate genres from top artists
      genres = [genre for artist in top_artists for genre in artist['genres']]
      genre_counts = Counter(genres)
      top_genres = genre_counts.most_common(5)




      # Save or update wrap data with top artists and genres
      wrap_data = {
          'step': step,
          'time_range': time_range_param,
          'top_artists': top_artists,
          'top_genres': top_genres,
      }
      if wrap:
          # Update existing wrap data
          wrap.wrap_data = json.dumps(wrap_data)
          wrap.save()
      else:
          # Create new wrap for today
          wrap = SpotifyWrap.objects.create(user=request.user, wrap_data=json.dumps(wrap_data), time_range=time_range_param)




  elif step == 6:
      # Fetch top albums for each top artist
      top_artists_data = fetch_spotify_data(top_artists_url, spotify_token, params=params)
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


      # Limit top_albums to the first 10 entries
      top_albums = top_albums[:10]


      # Save or update wrap data with top albums
      wrap_data = {
          'step': step,
          'time_range': time_range_param,
          'top_albums': top_albums,
      }
      if wrap:
          # Update existing wrap data
          wrap.wrap_data = json.dumps(wrap_data)
          wrap.save()
      else:
          # Create new wrap for today
          wrap = SpotifyWrap.objects.create(user=request.user, wrap_data=json.dumps(wrap_data), time_range=time_range_param)
  elif step == 8:
      # Retrieve top genres if they were saved in step 2
      if wrap and wrap.wrap_data:
          wrap_data = json.loads(wrap.wrap_data)
          top_genres = wrap_data.get('top_genres', [])


      # If top_genres wasn't saved, calculate it again (in case user skipped directly to step 4)
      if not top_genres:
          top_artists_data = fetch_spotify_data(top_artists_url, spotify_token, params=params)
          top_artists = [
              {
                  'name': artist['name'],
                  'genres': artist.get('genres', [])
              }
              for artist in top_artists_data.get('items', [])
          ]
          genres = [genre for artist in top_artists for genre in artist['genres']]
          genre_counts = Counter(genres)
          top_genres = genre_counts.most_common(10)


  # Handle "Save to Profile" submission
  if request.method == 'POST' and 'save' in request.POST:
      save_wrap_to_profile(request.user, wrap, time_range_param)
      print(f"Time Range in view_wraps (after form submission): {time_range}") # Debugging
      return render(request, "profile.html")


  # Render the wraps page with the collected data
  return render(request, 'wraps.html', {
      'step': step,
      'time_range': time_range_param,
      'top_tracks': top_tracks,
      'top_artists': top_artists,
      'top_genres': top_genres,
      'top_albums': top_albums,
      'creation_month_day': creation_month_day
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



from django.contrib.auth import logout

@login_required
def delete_account(request):
    """Allow user to delete their account."""
    if request.method == 'POST':
        user = request.user
        logout(request)  # Log out the user before deleting
        user.delete()  # Delete the user
        return redirect('register')  # Redirect to the registration page
    return render(request, 'delete_account.html')  # Optional: confirmation page





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



from django.shortcuts import render, get_object_or_404
from django.http import Http404
import json
from .models import SpotifyWrap, Profile

def view_old_wrap(request, wrap_id):
    """View for displaying details of a specific wrap based on wrap_id."""
    # Retrieve the wrap object by wrap_id
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id)

    # Check if the wrap belongs to the current user or a friend
    #is_mine = wrap.user == request.user
    # if not is_mine:
    #     user_profile = Profile.objects.get(user=request.user)
    #     if not user_profile.friends.filter(id=wrap.user.id).exists():
    #         raise Http404("You do not have permission to view this wrap.")

    # Load the wrap data from the database
    wrap_data = json.loads(wrap.wrap_data)

    # Ensure 'step' starts from 1 if not present
    step = wrap_data.get('step', 1)

    # Extract the necessary data from wrap_data
    time_range = wrap_data.get('time_range')
    top_tracks = wrap_data.get('top_tracks', [])
    top_artists = wrap_data.get('top_artists', [])
    top_genres = wrap_data.get('top_genres', [])
    top_albums = wrap_data.get('top_albums', [])

    # Render the wrap details in a template, including the 'is_mine' flag
    return render(request, 'view_old_wrap.html', {
        'wrap_id': wrap.id,
        'step': step,
        'time_range': time_range,
        'top_tracks': top_tracks,
        'top_artists': top_artists,
        'top_genres': top_genres,
        'top_albums': top_albums,
    })


def top_songs(request):
    # Assuming you have stored the user's Spotify access token in their session
    access_token = request.session.get('access_token')
    print(f"Access Token: {access_token}")

    if not access_token:
        # Redirect to login or ask user to connect their Spotify
        return redirect('spotify_login')

    # Retrieve time_range from session, default to 'short_term'
    time_range = request.session.get('time_range', 'short_term')
    print(f"Time Range from Session: {time_range}")

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # API endpoint with the time_range parameter
    url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_range}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        top_tracks = response.json().get('items', [])

        # Process the top tracks to add album images
        for track in top_tracks:
            if track.get('album') and track['album'].get('images'):
                track['album_image'] = track['album']['images'][0]['url']
            else:
                track['album_image'] = None  # No image available
    else:
        top_tracks = []

    context = {
        'top_tracks': top_tracks,
        'time_range': time_range  # Pass the time_range to the context
    }
    return render(request, 'top_songs.html', context)
