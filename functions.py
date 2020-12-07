from spotipy import oauth2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from secrets import client_id, client_secret

# GLOBAL CONSTANTS

# AUTHORIZATION
AUTH = oauth2.SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST REQUEST
AUTH_RESPONSE = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

# CONVERT RESPONSE TO JSON
AUTH_RESPONSE_DATA = AUTH_RESPONSE.json()

# SAVE ACCESS TOKEN
ACCESS_TOKEN = AUTH_RESPONSE_DATA['access_token']

HEADERS = {
    'Authorization': 'Bearer {token}'.format(token=ACCESS_TOKEN)
}

BASE_URL = 'https://api.spotify.com/v1/'

ARTIST_ID = "1a4N2lwra7WGjwCDJS1Dkk"


def get_artist_tracks():
    # GET REQUEST
    r = requests.get(BASE_URL + 'artists/' + ARTIST_ID + '/albums',
                     headers=HEADERS,
                     params={'include_groups': 'album', 'limit': 50})

    d = r.json()

    data = []  # HOLDS TRACK INFO
    albums = []  # HOLDS ALBUMS (NO DUPLICATES)

    # LOOP OVER ALBUMS FOR TRACKS
    for album in d['items']:
        album_name = album['name']
        print(album_name)

        # GET TRACKS FROM ALBUM
        r = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks',
                         headers=HEADERS)
        tracks = r.json()['items']

        for track in tracks:
            # GET AUDIO FEATURES (KEY, DANCEABILITY, ETC.)
            f = requests.get(BASE_URL + 'audio-features/' + track['id'],
                        headers=HEADERS)
            f = f.json()

            # COLLECT ALL ALBUM INFO
            f.update({
                'track_name': track['name'],
                'album_name': album_name,
                'release_date': album['release_date'],
                'album_id': album['id']
            })

            data.append(f)
    return data


def visualize_audio(track_data):
    # NOW TIME FOR DATAFRAMES
    df = pd.DataFrame(track_data)
    # CONVERT RELEASE DATE TO ACTUAL DATE AND SORT
    df['release_date'] = pd.to_datetime(df['release_date'])
    df = df.sort_values(by='release_date')
    df.head()

    plt.figure(figsize=(10, 10))

    # BUILD SCATTER PLOT
    ax = sns.scatterplot(data=df, x='instrumentalness', y='speechiness',
                         hue='album_name', palette='rainbow',
                         size='duration_ms', sizes=(50, 1000),
                         alpha=0.7)

    # DISPLAY LEGEND WITH NO SIZE ATTRIBUTE
    h, labs = ax.get_legend_handles_labels()
    ax.legend(h[1:10], labs[1:10], loc='best', title=None)
    ax.legend()
    ax.grid(True)
    plt.show()


if __name__ == '__main__':
    track_data = get_artist_tracks()
    visualize_audio(track_data)