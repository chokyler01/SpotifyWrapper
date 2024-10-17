# spotify_token.py
import time
import requests

# Spotify credentials
CLIENT_ID = 'e1c53cf948ff4cddaa379b88861b2714'
CLIENT_SECRET = '5d13bd1a4a1c41e193d7546b4b9585b6'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Store access token and its expiration time
access_token = None
expires_at = None

def get_token():
    global access_token, expires_at
    response = requests.post(TOKEN_URL, data={
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    token_info = response.json()
    access_token = token_info['access_token']
    expires_in = token_info['expires_in']  # Expiry time in seconds
    expires_at = time.time() + expires_in  # Current time + expiry time
    print(f"New token acquired, expires at {expires_at}")

def get_valid_token():
    global access_token, expires_at
    # Check if token is expired
    if not access_token or time.time() > expires_at:
        print("Token expired, requesting a new one...")
        get_token()
    else:
        print("Token is still valid.")
    return access_token

# Generic function to fetch data from any Spotify API endpoint
def fetch_spotify_data(endpoint):
    token = get_valid_token()  # Ensure the token is valid
    headers = {
        'Authorization': f'Bearer {token}'
    }
    # Make a request to the given endpoint
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f'Failed to fetch data: {response.status_code}'}
