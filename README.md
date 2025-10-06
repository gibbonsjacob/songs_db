# Building Your First Data Pipeline (Medium Series)

Welcome! This repository accompanies my Medium series on **building a data pipeline from scratch**. In this project, we focus on education and practicality, showing how anyone can structure, clean, and insert data in a repeatable way, even without enterprise-scale infrastructure. Specifically, we'll be pulling music data from Spotify:  playlists, tracks, albums, and artists. Then, we'll parse and normalize it,  and finally load it into a relational database. The goal is to demonstrate how to turn raw API data into a clean, usable dataset while highlighting good design and modularity practices. In the final part of this series (where we are now!) we'll put all that data to use by finding a matching music video on Youtube for each track found in our Spotify playlist.

<br>

<br>

### The Medium series walks you through **four parts**:

1. **Part 1:** Fetching data from Spotify
2. **Part 2:** Designing an intelligent database schema
3. **Part 3:** Inserting and managing data efficiently 
4. **Part 4:** Using our data for something fun (where we are now!)

This repository contains the code, SQL queries, and examples for **Parts 1–4**, including:

* Reusable **Database class** for safe connections and query execution
* Spotify fetchers for **playlists, tracks, albums, and artists** with batching and pagination
* Parsing functions to **flatten nested JSON** into clean pandas DataFrames
* SQL + pandas workflow to **insert only new rows** into your database
* Handling of **relationships** like track-to-artist and artist-to-genre in a repeatable
* Pipeline that creates a search query and **searches Youtube** for a matching music video per track from our playlist

## Project Highlights

* **Educational Focus:** Every function and SQL snippet is intended to be understandable, modular, and reusable. This is not just code. It’s a teaching tool!
* **Anyone Can Do This:** You don’t need specialized infrastructure; a local SQLite database is enough to follow along and learn the concepts.
* **Modular & Repeatable:** Each step builds on the last, making it easy to expand or replicate for other data sources.
* **Separation of Concerns:** SQL lives in separate files, Python handles parsing, and the pipeline is designed to be clear, testable, and maintainable.

## Usage

1. **Clone this repository**:

```bash
git clone https://github.com/gibbonsjacob/songs_db.git
cd songs_db
```

2. **Install dependencies** (Python 3.12 recommended):

```bash
uv pip install -r pyproject.toml
```

3. **Register Spotify App**

    - See [Building Your First Data Pipeline (Part 1/4)
    ](https://medium.com/python-in-plain-english/building-your-first-data-pipeline-apis-arent-scary-part-1-4-eefbf033d056) for instructions on this
        - This article also covers what to do with your client_id and client_secret from Spotify

4. **Set up a Project in Google Cloud Console**: 
    -   Follow the Instructions outlined in [google_project_setup.md](./google_project_setup.md) to establish your own Google Project
    - We do this so the 100 searches per day limit is ***per user*** 
5.  **Find All User Playlists**

    ```bash
    uv run spotify_fetcher.py --get-playlists
    ```

    - Note that you can also just copy / paste the playlist name from Spotify directly
    - Add this value to the `playlist_of_interest` variable in the configs section of  [main.py](./main.py)
6. Run [main.py](./main.py)

    ```bash
    uv run main.py
    ```

    - This will write Youtube URLs to fact_youtube_search

## Directory Structure (Through Part 4)

``` text
songs_db/
├── db_management.py
├── get_video_url.py
├── google_project_setup.md
├── main.py
├── pyproject.toml
├── README.md
├── songs/
│   ├── sql_queries/
│   │   ├── distinct_album_id.sql
│   │   ├── distinct_artist_id.sql
│   │   ├── distinct_track_id.sql
│   │   ├── get_new_albums.sql
│   │   ├── get_new_artists.sql
│   │   └── get_tracks_to_search.sql
│   └── table_defs/
│       ├── dim_album.sql
│       ├── dim_artist.sql
│       ├── dim_song.sql
│       ├── xref_artist_genres.sql
│       └── xref_song_to_artist.sql
├── spotify_fetcher.py
└── uv.lock
```

## Notes

* This repository is tied to the Medium series. Code examples may reference article sections.

## Contributions

This project is primarily educational and intended for personal learning. Feedback is welcome, but please **do not submit production-level changes** without discussion.
