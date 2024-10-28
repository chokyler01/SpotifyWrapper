import requests


# Generic function to fetch data from any Spotify API endpoint
def fetch_spotify_data(endpoint, access_token, params=None):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f'Failed to fetch data: {response.status_code}'}
