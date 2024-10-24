import requests


# Generic function to fetch data from any Spotify API endpoint
def fetch_spotify_data(endpoint, access_token):
   headers = {
       'Authorization': f'Bearer {access_token}'
   }


   # Make a request to the given endpoint
   response = requests.get(endpoint, headers=headers)
   if response.status_code == 200:
       return response.json()
   else:
       return {'error': f'Failed to fetch data: {response.status_code}'}

