# prune-scrobbles
A collection of python scripts to prune scrobbles (or listens) for submitting to ListenBrainz.

## Why
I had exported listening data from multiple music streaming services and wanted to remove skipped tracks from the files. Streaming services like, Spotify and YouTube Music will keep a record of every single track played regardless of the length of time the track was played.

## Spotify
1. `spotify-filter.py` will take the JSON files from the "Spotify Extended Streaming History" [export](https://support.spotify.com/us/article/understanding-your-data/) and remove any skipped tracks. Skipped tracks are songs played for less than 30 seconds.  You can change the time value in the python script file to reflect your needs.
2. With the resulting JSON files you can submit the cleaned-up listens to ListenBrainz with their default tool to by going to [Import listens](https://listenbrainz.org/settings/import/).

## YouTube Music
1. `ytm-filter-music-and-topic.py` will take your Google Takeout YouTube Watch History (`watch-history.html`) export and remove any video watch listings and only keep YouTube Music listens and videos with a music topic.
2. `ytm_remove_30s_skips.py` will take the resulting listens, from step 1, and remove any tracks that were played for less then 30 seconds. Again, you can change the time value in the python script to reflect your needs.
3. Once you have the resulting HTML file you can submit the cleaned-up listens to ListenBrainz with [ytm-extractor](https://github.com/defvs/ytm-extractor). You'll need your [ListenBrainz API Key - User Token](https://listenbrainz.readthedocs.io/en/latest/users/api/index.html).



Note, these scripts were made with the help of ChatGPT. I don't know how to code python.
