# 🧠 Building Your First Data Pipeline (Medium Series)

Welcome! This repository accompanies my Medium series on **building a data pipeline from scratch**. In this project, we focus on education and practicality, showing how anyone can structure, clean, and insert data in a repeatable way—even without enterprise-scale infrastructure.  

Specifically, we’ve been pulling music data from Spotify: playlists, tracks, albums, and artists. Then we’ve parsed and normalized it, and finally loaded it into a relational database.  

Now, in **Part 4**, we’re putting all that data to use by finding a **matching YouTube music video** for each track in our playlist.

<br>

<br>

### 🪜 The Medium series walks you through **four parts**:

1. **Part 1:** Fetching data from Spotify  
2. **Part 2:** Designing an intelligent database schema  
3. **Part 3:** Inserting and managing data efficiently  
4. **Part 4:** Using our data for something fun: **finding YouTube videos!**

This repository contains the code, SQL queries, and examples for **Parts 1–4**, including:

* Reusable **Database class** for safe connections and query execution  
* Spotify fetchers for **playlists, tracks, albums, and artists** with batching and pagination  
* Parsing functions to **flatten nested JSON** into clean pandas DataFrames  
* SQL + pandas workflow to **insert only new rows** into your database  
* Handling of **relationships** like track-to-artist and artist-to-genre in a repeatable way  
* **YouTube integration** that builds search queries, authenticates with Google, and stores video URLs for each track  

## Project Highlights

* **Educational Focus:** Every function and SQL snippet is intended to be understandable, modular, and reusable. This is not just code. It’s a teaching tool!
* **Anyone Can Do This:** You don’t need specialized infrastructure; a local SQLite database is enough to follow along and learn the concepts.
* **Modular & Repeatable:** Each step builds on the last, making it easy to expand or replicate for other data sources.
* **Separation of Concerns:** SQL lives in separate files, Python handles parsing, and the pipeline is designed to be clear, testable, and maintainable.

## 🎬 What’s New in Part 4

Part 4 introduces our **YouTube search pipeline**, which connects your Spotify data to real YouTube results.

Here’s what happens step-by-step:

1. **Identify Tracks to Search**  
   We query our database for tracks without an existing `youtube_url` (via `get_tracks_to_search.sql`).

2. **Build Search Queries**  
   For each song, we join its artists back together (using `' x '` as a separator) and generate queries like:  

   ``` text
   <track_name> - <artist_name> (Official Music Video)
   ```

3. **Search YouTube via API**  
   Using the Google API Client, we authenticate locally with OAuth 2.0 (`client_secret.json` + `token.pickle`) and execute YouTube Search API calls to retrieve video IDs.

4. **Handle Results and Errors**  
   Successful searches are stored in `fact_youtube_search`, while errors (like rate limits) are logged separately for analysis and retry.

5. **Store Results for Downstream Use**  
   The resulting URLs are inserted into our fact table so future analytics or playlists can directly reference the official video.

> 💡 **Why separate this step?**  
> Keeping YouTube logic separate preserves database independence — the same schema can serve other downstream use cases without modification.

---


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
    - This page will also walk through how to authenticate your project with OAuth2.0
5.  **Find All User Playlists**

    ```bash
    uv run spotify_fetcher.py --get-playlists
    ```

    - Note that you can also just copy / paste the playlist name from Spotify directly
    - Add this value to the `playlist_of_interest` variable in the configs section of  [main.py](./main.py)


6. **Authenticate with Google** 
    - 
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
│       ├── fact_batch_execution.sql
│       ├── fact_error_log.sql
│       ├── fact_youtube_search.sql
│       ├── xref_artist_genres.sql
│       └── xref_song_to_artist.sql
├── spotify_fetcher.py
└── uv.lock
```

## Notes

* This repository is tied to the Medium series. Code examples may reference article sections.

## Contributions

This project is primarily educational and intended for personal learning. Feedback is welcome, but please **do not submit production-level changes** without discussion.
