# prune-scrobbles
A collection of python scripts to prune scrobbles (or listens) for submitting to ListenBrainz.

## Why
I had exported listening data from multiple music streaming services and wanted to remove skipped tracks from the files. Streaming services like, Spotify and YouTube Music will keep a record of every single track played regardless of the length of time the track was played.

## Spotify
`spotify-filter.py` will take the JSON files from the "Spotify Extended Streaming History" export and remove any skipped tracks longer than 30 seconds. You can change the time value in the python script file to reflect your needs.

## YouTube Music
1. `ytm-filter-music-and-topic.py` will take your Google Takeout YouTube Watch History (`watch-history.html`) export and remove any video watch listings and only keep YouTube Music listens and videos with a music topic.
2. `ytm_remove_30s_skips.py` will take the resulting listens, from step 1, and remove any tracks that were played for less then 30 seconds. Again, you can change the time value in the python script to reflect your needs.

Note, these scripts were made with the help of ChatGPT. I don't know how to code python.
