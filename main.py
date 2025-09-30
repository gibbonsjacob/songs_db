import pandas as pd
import spotify_fetcher
from db_management import Database
from pathlib import Path




############################ CONFIGS ##############################

playlist_of_interest = '<playlist_name>'



###################################################################



def check_for_tables(songs_db, tables: list) -> dict:
    """
    Check for existence of core tables (defined below) 

    Args:
        songs_db (sqlite3 database): Database file housing all related information
        tables (list): List of tables to check for
    Returns:
        Dict: Keys = values from tables, Values = T/F regarding whether the object exists or not
    """
    table_existence = {}

    for table in tables:
        sql_template = f"""
        
            SELECT 1 
            FROM sqlite_master 
            WHERE type='table' AND name='{table}';
        
        """

        temp = songs_db.select_sql(sql_template)

        table_existence[table] = (isinstance(temp, pd.DataFrame) 
                                  and not temp.empty)
        
    return table_existence



def parse_tracks(items: list[dict]) -> pd.DataFrame:
    """Extract normalized track fields from raw Spotify track payloads."""
    records = []

    for item in items:
        track = item.get("track", {})
        if not track:
            continue

        records.append({
            "track_id": track.get("id"),
            "track_name": track.get("name"),
            "isrc": track.get("external_ids", {}).get("isrc"),
            "duration_ms": track.get("duration_ms"),
            "explicit": int(track.get("explicit", False)),  # convert bool → int
            "popularity": track.get("popularity"),
            "disc_number": track.get("disc_number"),
            "track_number": track.get("track_number"),
            "preview_url": track.get("preview_url"),
            "spotify_url": track.get("external_urls", {}).get("spotify"),
            "track_uri": track.get("uri"),
            "added_to_playlist": item.get("added_at"),
            "album_id": track.get("album", {}).get("id")
        })

    df = pd.DataFrame.from_records(records).drop_duplicates(subset=["track_id"])
    return df


def parse_albums(items: list) -> pd.DataFrame:
    """
    Extract normalized album fields from raw Spotify album payloads.

    Args:
        items (list): List of raw album payloads (dicts).
    
    Returns:
        pd.DataFrame: Normalized album information for dim_album.
    """
    records = []

    for album in items:
        if not album:
            continue
        records.append({
            "album_id": album.get("id"),
            "album_name": album.get("name"),
            "album_type": album.get("album_type"),
            "release_date": album.get("release_date"),
            "release_date_precision": album.get("release_date_precision"),
            "total_tracks": album.get("total_tracks"),
            "spotify_url": album.get("external_urls", {}).get("spotify"),
            "href": album.get("href"),
            "type": album.get("type"),
            "uri": album.get("uri")
        })

    return pd.DataFrame.from_records(records).drop_duplicates(subset=['album_id'])




def parse_artists(items: list[dict]) -> tuple:
    """
    Extract normalized artist fields from raw Spotify artist payloads.
    
    Args:
        items (list): List of raw artist payloads (dicts).
    
    Returns:
        pd.DataFrame: Normalized artist information.
    """
    artist_records = []
    genre_records = []


    for artist in items:
        if not artist:
            continue
        artist_records.append({
            "artist_id": artist.get("id"),
            "artist_name": artist.get("name"),
            "artist_url": artist.get("external_urls", {}).get("spotify"),
            "artist_href": artist.get("href"),
            "popularity": artist.get("popularity"),
            "artist_type": artist.get("type"),
            "artist_uri": artist.get("uri"),
            "followers_total": artist.get("followers", {}).get("total"),
        })

        # Doing genre mappings here too so we don't have to parse the artist payload twice
        for genre in artist.get("genres", []):
            genre_records.append({
                "artist_id": artist.get("id"),
                "genre_name": genre
            })



    artists_df = pd.DataFrame.from_records(artist_records).drop_duplicates(subset=["artist_id"])
    artist_genres = pd.DataFrame.from_records(genre_records).drop_duplicates(subset=['artist_id', 'genre_name'])

    return artists_df, artist_genres



def parse_song_to_artist_map(items: list[dict]) -> pd.DataFrame:
    """Extract normalized artist to track maps from raw Spotify track payloads."""

    records = []

    for item in items:
        track = item.get("track", {})
        track_id = track.get("id")
        for artist in track.get("artists", []):
            artist_id = artist.get("id")
            if track_id and artist_id:
                records.append((track_id, artist_id))

    
    df = pd.DataFrame(records, columns=["track_id", "artist_id"]).drop_duplicates()
    return df




def main():



    ## Database stuff 
    songs_db = Database('songs/songs_management.db')
    tables_path = Path('songs/table_defs/')

    #key is the table name, value is the CREATE TABLE sql statement in the file
    tables = {filepath.stem: filepath.read_text() for filepath in tables_path.iterdir() if filepath.is_file()}

    table_existence = check_for_tables(songs_db, tables.keys())

    for table, existence in table_existence.items():
        if not existence:
            #if table doesn't exist, run the create table sql 
            #this should only ever hit the very first time we run
            songs_db.execute_sql(tables[table])



    ### Next let's get all songs from our playlist of interest
    all_playlists = spotify_fetcher.get_user_playlists()
    playlist_to_iterate = [p for p in all_playlists if p.get('name') == playlist_of_interest][0].get('url')

    
    raw_track_payload = spotify_fetcher.get_song_details(playlist_to_iterate)

    # some cleanup because this is messy 
    all_tracks = parse_tracks(raw_track_payload)
    song_to_artist_map = parse_song_to_artist_map(raw_track_payload)


    ## Now let's get a list of the tracks, albums, and artists we already have in our db
    ## we can skip the xref because if we already have the track we have the xref

    existing_songs = songs_db.select_sql(Path('songs/sql_queries/distinct_track_id.sql').read_text())


    ## left join existing songs with all_songs to figure out which ones are new, then drop
    ## all the existing ones that match both df's so we're left with only new songs
    new_songs = all_tracks.merge(existing_songs, on="track_id", how='left', indicator=True)
    new_songs = new_songs[new_songs['_merge'] == 'left_only'].drop(columns=['_merge'])
    if not new_songs.empty:
        new_songs_insert_sql = songs_db.build_insert_into_sql('dim_song', new_songs)
        songs_db.execute_sql(new_songs_insert_sql)


    ## Next we'll handle the track to artist map - this will also let us cheat a bit downstream by doing this now 
    ## Here we'll leverage SQL's ON CONFLICT clause rather than building new unique pairs
    ## There's no real reason to go either way, I just thought of it here
    song_to_artist_map_insert_sql = songs_db.build_insert_into_sql(
                                    dest_table='xref_song_to_artist',
                                    df=song_to_artist_map, 
                                    on_conflict=f"(track_id, artist_id) DO NOTHING")

    songs_db.execute_sql(song_to_artist_map_insert_sql)



    ## Now let's handle albums - we can cheat a little here and only use SQL
    ## since we've already inserted all our new tracks, we can just compare album_ids
    ## that exist in dim_song vs. those that exist in dim_album and then hit the API 
    ## endpoint for any album_id's that are leftover
    existing_albums = songs_db.select_sql(Path('songs/sql_queries/distinct_album_id.sql').read_text())
    new_album_ids = songs_db.select_sql(Path('songs/sql_queries/get_new_albums.sql').read_text())['album_id'].to_list()    
    raw_albums_payload = spotify_fetcher.get_album_details(new_album_ids)
    cleaned_albums = parse_albums(raw_albums_payload)
    if not cleaned_albums.empty: 
        new_albums_insert_sql = songs_db.build_insert_into_sql('dim_album', cleaned_albums)
        songs_db.execute_sql(new_albums_insert_sql)
    




    ### Finally we handle artists and genres - we can do this exactly the same way as we did albums
    ### we'll cheat by comparing what's in our xref table to what's in dim_artist - anything that's
    ### in our xref table but not in dim_artist is a "new" artist
    existing_artists =  songs_db.select_sql(Path('songs/sql_queries/distinct_artist_id.sql').read_text())
    new_artist_ids = songs_db.select_sql(Path('songs/sql_queries/get_new_artists.sql').read_text())['artist_id'].to_list()    
    raw_artist_payload = spotify_fetcher.get_artist_details(new_artist_ids)
    cleaned_artists, artist_genres = parse_artists(raw_artist_payload)
    if not cleaned_artists.empty:
        new_artist_insert_sql = songs_db.build_insert_into_sql('dim_artist', cleaned_artists)
        songs_db.execute_sql(new_artist_insert_sql)

    if not artist_genres.empty:

        new_genre_insert_sql = songs_db.build_insert_into_sql(
                                        dest_table='xref_artist_genres',
                                        df = artist_genres, 
                                        on_conflict='(artist_id, genre_name) DO NOTHING', 
                                        )
        songs_db.execute_sql(new_genre_insert_sql)





if __name__ == "__main__":
    main()
