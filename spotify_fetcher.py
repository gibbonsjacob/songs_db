import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os 


def load_env_vars():
    load_dotenv()
    spotify_client_id = os.getenv('spotify_client_id')
    spotify_client_secret = os.getenv('spotify_client_secret')
    spotify_redirect_url = os.getenv('spotify_redirect_url')
    return spotify_client_id, spotify_client_secret, spotify_redirect_url



###### CONFIGS ######

spotify_client_id, spotify_client_secret, spotify_redirect_url, base_dir = load_env_vars()
scopes = """
        user-read-private
        user-read-email
        playlist-read-private 
        playlist-read-collaborative 
        """

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id,
                                            client_secret=spotify_client_secret,
                                            redirect_uri=spotify_redirect_url,
                                            scope=scopes))

artist_id_limit = 50
album_id_limit = 20






def get_user_playlists():
    """Retrieve all playlists from the user's Spotify account with names and URLs."""
    playlists = sp.current_user_playlists()

    
    return [
        {"name": playlist["name"], "url": playlist["external_urls"]["spotify"]}
        for playlist in playlists["items"]
    ]




def get_song_details(playlist_url):
    """Fetch song details for every track in a Spotify playlist.
        limit of 100 ID's per call"""
    
    playlist_id = playlist_url.split("/")[-1].split("?")[0]  # Playlist ID from URL
    results = []
    offset = 0
    limit = 100  

    ## because this endpoint is paginated, we call it as many times 
    ## as we need to until there's no tracks left to hit
    while True:
        response = sp.playlist_items(
            playlist_id,
            offset=offset,
            limit=limit
        )
        items = response.get("items", [])
        results.extend(items)

        # If fewer than 'limit' items returned, we’re at the end
        if len(items) < limit:
            break

        offset += limit

    return results
    


def get_album_details(album_ids: list):
    """ limit of 20 ID's per call"""

    results = []
    for i in range(0, len(album_ids), album_id_limit):
        chunk = album_ids[i:i + album_id_limit]
        resp = sp.albums(chunk)
        results.extend(resp.get('albums', []))
         
    return results



def get_artist_details(artist_ids: list):
    """ Limit of 50 ID's per call so we batch our calls """
    results = []
    for i in range(0, len(artist_ids), artist_id_limit):
        chunk = artist_ids[i:i + artist_id_limit]
        resp = sp.artists(chunk)
        results.extend(resp.get('artists', []))
         
    return results



    


