# Building Your First Data Pipeline (Medium Series)

Welcome! This repository accompanies my Medium series on **building a data pipeline from scratch**. In this project, we focus on education and practicality, showing how anyone can structure, clean, and insert data in a repeatable way, even without enterprise-scale infrastructure. Specifically, we'll be pulling music data from Spotify:  playlists, tracks, albums, and artists. Then, we'll parse and normalize it,  and finally load it into a relational database. The goal is to demonstrate how to turn raw API data into a clean, usable dataset while highlighting good design and modularity practices.

<br>

<br>

### The Medium series walks you through **four parts**:

1. **Part 1:** Fetching data from Spotify
2. **Part 2:** Designing an intelligent database schema
3. **Part 3:** Inserting and managing data efficiently (where we are now!)
4. **Part 4:** Using your data for analysis, enrichment, or automation (coming soon)

This repository contains the code, SQL queries, and examples for **Parts 1–3**, including:

* Reusable **Database class** for safe connections and query execution
* Spotify fetchers for **playlists, tracks, albums, and artists** with batching and pagination
* Parsing functions to **flatten nested JSON** into clean pandas DataFrames
* SQL + pandas workflow to **insert only new rows** into your database
* Handling of **relationships** like track-to-artist and artist-to-genre in a repeatable

## Project Highlights

* **Educational Focus:** Every function and SQL snippet is intended to be understandable, modular, and reusable. This is not just code. It’s a teaching tool!
* **Anyone Can Do This:** You don’t need specialized infrastructure; a local SQLite database is enough to follow along and learn the concepts.
* **Modular & Repeatable:** Each step builds on the last, making it easy to expand or replicate for other data sources.
* **Separation of Concerns:** SQL lives in separate files, Python handles parsing, and the pipeline is designed to be clear, testable, and maintainable.

## Getting Started

1. Clone this repository:

```bash
git clone https://github.com/gibbonsjacob/songs_db.git
cd songs_db
```

2. Install dependencies (Python 3.12 recommended):

```bash
uv pip install -r pyproject.toml
```

3. Follow along with the Medium series to understand **why each part exists**, how the pieces interact, and the design choices behind the pipeline.

## Directory Structure (Through Part 3)

``` text
songs_db/
├── db_management.py
├── .env
├── main.py
├── pyproject.toml
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
* Part 4 will focus on **applying the data**, including using it to find YouTube music videos for each track.

## Contributions

This project is primarily educational and intended for personal learning. Feedback is welcome, but please **do not submit production-level changes** without discussion.
