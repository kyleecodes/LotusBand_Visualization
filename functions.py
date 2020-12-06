from spotipy import oauth2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from secrets import client_id, client_secret

# AUTHORIZATION
auth = oauth2.SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST REQUEST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

# CONVERT RESPONSE TO JSON
auth_response_data = auth_response.json()

# SAVE ACCESS TOKEN
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# GET REQUEST
BASE_URL = 'https://api.spotify.com/v1/'

artist_id = "1a4N2lwra7WGjwCDJS1Dkk"


def get_artist_tracks():
    r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
                     headers=headers,
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
                         headers=headers)
        tracks = r.json()['items']

        for track in tracks:
            # GET AUDIO FEATURES (KEY, DANCEABILITY, ETC.)
            f = requests.get(BASE_URL + 'audio-features/' + track['id'],
                        headers=headers)
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