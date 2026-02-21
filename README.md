# prune-scrobbles
A collection of python scripts to prune listen data from streaming audio services. Then, you can use the resulting clean data files for submitting to ListenBrainz.

## Why
I had exported listening data from multiple music streaming services and wanted to remove skipped tracks from the files. Streaming services, like Spotify and YouTube Music, will keep a record of every single track played regardless of the length of time the track was played.

Tracks that were played for 10 to 15 seconds were generally tracks that I had chosen to skip in my scrobbling or listening histories. I used the scripts below to clean my data and removed those skipped or duplicate tracks listed before I added them into my ListenBrainz account.

## Spotify
1. `spotify-filter.py` will take the JSON files from the "Spotify Extended Streaming History" [export](https://support.spotify.com/us/article/understanding-your-data/) and remove any skipped tracks. Skipped tracks are songs played for less than 30 seconds.  You can change the time value in the python script file to reflect your needs.
2. With the resulting JSON files you can submit the cleaned-up listens to ListenBrainz with their default tool to by going to [Import listens](https://listenbrainz.org/settings/import/).

It's worth nothing that the ListenBrainz default import tool does this de-duplication automatically. I got similar import numbers after removing skipped tracks.

## YouTube Music
1. `ytm-filter-music-and-topic.py` will take your Google Takeout YouTube Watch History (`watch-history.html`) export and remove any video watch listings and only keep YouTube Music listens and videos with a music topic.
2. `ytm_remove_30s_skips.py` will take the resulting listens, from step 1, and remove any tracks that were played for less then 30 seconds. Again, you can change the time value in the python script to reflect your needs.
3. Once you have the resulting HTML file you can submit the cleaned-up listens to ListenBrainz with [ytm-extractor](https://github.com/defvs/ytm-extractor). You'll need your [ListenBrainz API Key - User Token](https://listenbrainz.readthedocs.io/en/latest/users/api/index.html).

Choosing 60 seconds for filtering-out an removing track listings was a much better balance and helped clean up time shifted scrobbles.

Optionally, use `ytm_remove_60s_skips.py` to be more aggresive with filtering and remove any repeated listens in a 60 second window.

Note, these scripts were made with the help of ChatGPT. I don't know how to code python.
