import spotipy
import configparser
import json
import requests
from spotipy import oauth2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy

config = configparser.ConfigParser()
config.read('config.cfg')
client_id = config.get('SPOTIFY', 'CLIENT_ID')
client_secret = config.get('SPOTIFY', 'CLIENT_SECRET')

auth = oauth2.SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

# track_id = '6y0igZArWVi6Iz0rj35c1Y'
#
# r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)
#
# r = r.json()
# print(r)

artist_id = "1a4N2lwra7WGjwCDJS1Dkk"

r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
                 headers=headers,
                 params={'include_groups': 'album', 'limit': 50})
d = r.json()

data = []  # will hold all track info
albums = []  # to keep track of duplicates

# loop over albums and get all tracks
for album in d['items']:
    album_name = album['name']
    print(album_name)

    # pull all tracks from this album
    r = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks',
                     headers=headers)
    tracks = r.json()['items']

    for track in tracks:
        # get audio features (key, liveness, danceability, ...)
        f = requests.get(BASE_URL + 'audio-features/' + track['id'],
                         headers=headers)
        f = f.json()

        # combine with album info
        f.update({
            'track_name': track['name'],
            'album_name': album_name,
            'release_date': album['release_date'],
            'album_id': album['id']
        })

        data.append(f)

df = pd.DataFrame(data)
# convert release_date to an actual date, and sort by it
df['release_date'] = pd.to_datetime(df['release_date'])
df = df.sort_values(by='release_date')
df.head()

plt.figure(figsize=(10, 10))

ax = sns.scatterplot(data=df, x='instrumentalness', y='speechiness',
                     hue='album_name', palette='rainbow',
                     size='duration_ms', sizes=(50, 1000),
                     alpha=0.7)

# display legend without `size` attribute
h, labs = ax.get_legend_handles_labels()
ax.legend(h[1:10], labs[1:10], loc='best', title=None)
ax.legend()
ax.grid(True)
plt.show()