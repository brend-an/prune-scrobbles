```
██████╗ ██████╗ ██╗   ██╗███╗   ██╗███████╗
 ██╔══██╗██╔══██╗██║   ██║████╗  ██║██╔════╝
 ██████╔╝██████╔╝██║   ██║██╔██╗ ██║█████╗  
 ██╔═══╝ ██╔══██╗██║   ██║██║╚██╗██║██╔══╝  
 ██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗
 ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
                                              
 ███████╗ ██████╗██████╗  ██████╗ ██████╗ ██████╗ ██╗     ███████╗███████╗
 ██╔════╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝
 ███████╗██║     ██████╔╝██║   ██║██████╔╝██████╔╝██║     █████╗  ███████╗
 ╚════██║██║     ██╔══██╗██║   ██║██╔══██╗██╔══██╗██║     ██╔══╝  ╚════██║
 ███████║╚██████╗██║  ██║╚██████╔╝██████╔╝██████╔╝███████╗███████╗███████║
 ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝
```
A collection of python scripts to prune listen data from streaming audio services and verify ListenBrainz data. Then, you can use the resulting clean data files for submitting (or re-submitting) to ListenBrainz.

## Why
I had exported listening data from multiple music streaming services and wanted to remove skipped tracks from the files. Streaming services, like Spotify and YouTube Music, will keep a record of every single track played regardless of the length of time the track was played.

Tracks that were played for 10 to 15 seconds were generally tracks that I had chosen to skip in my scrobbling or listening histories. I used the scripts below to clean my data and removed those skipped or duplicate tracks listed before I added them into my ListenBrainz account.

## Spotify
1. `spotify-filter.py` will take the JSON files from the "Spotify Extended Streaming History" [export](https://support.spotify.com/us/article/understanding-your-data/) and remove any skipped tracks. Skipped tracks are songs played for less than 30 seconds.  You can change the time value in the python script file to reflect your needs.
2. With the resulting JSON files you can submit the cleaned-up listens to ListenBrainz with their default tool to by going to [Import listens](https://listenbrainz.org/settings/import/).

Usage:
```
python spotify-filter.py
```

It's worth nothing that the ListenBrainz default import tool does this de-duplication automatically. I got similar import numbers after removing skipped tracks.

## YouTube Music
1. `ytm-filter-music-and-topic.py` will take your Google Takeout YouTube Watch History (`watch-history.html`) export and remove any video watch listings and only keep YouTube Music listens and videos with a music topic.

Usage:
```
python ytm-filter-music-and-topic.py
```

2. `ytm_remove_30s_skips.py` will take the resulting listens, from step 1, and remove any tracks that were played for less then 30 seconds. Again, you can change the time value in the python script to reflect your needs.

Usage:
```
python ytm_remove_30s_skips.py
```

3. Once you have the resulting HTML file you can submit the cleaned-up listens to ListenBrainz with [ytm-extractor](https://github.com/defvs/ytm-extractor). You'll need your [ListenBrainz API Key - User Token](https://listenbrainz.readthedocs.io/en/latest/users/api/index.html).

Choosing 60 seconds for filtering-out an removing track listings was a much better balance and helped clean up time shifted scrobbles.

Optionally, use `ytm_remove_60s_skips.py` to be more aggresive with filtering and remove any repeated listens in a 60 second window.

## ListenBrainz

### ListenBrainz Export Script
`listenbrainz_export_full_listens.py` exports all listens for a given user using the ListenBrainz API. Supports automatic resume and safe incremental writes.
Dependencies: `pip install requests`.

Usage:
```
    python listenbrainz_export_full_listens.py --username USER --token TOKEN
```
Optional:
```
    --output filename.json
```

Once your export is completed, and you have a complete `USER_export_full.json` JSON file, you can now audit this data and see if you have duplicates, skips or other data anomalies. This is useful if you want to clean and re-import the listening data or move your existing listening data to a new account.

###  ListenBrainz Audit Analyzer
`listenbrainz_audit_analyzer.py` does an analysis of the ListenBrainz user export JSON file and generates a comprehensive integrity report.

It calculates:
- Total listens
- Unique track count
- Exact duplicates
- Top artists
- Yearly distribution
- Skip counts (≤5s, ≤10s, ≤15s, ≤30s, ≤60s, ≤90s)
- Duration distribution
- Rapid burst detection (listens occurring within N seconds)

Usage:
```
    python listenbrainz_audit_analyzer.py export.json
```
Optional:
```
    --near-window 10   # near duplicate window in seconds
```

### ListenBrainz Audit v2
This script performs deep integrity analysis on a ListenBrainz export JSON.

This analyzer audits a ListenBrainz export for structural integrity, temporal plausibility, metadata quality, and listening diversity.

It helps detect:
- Duplicate imports
- Re-scrobbles
- Batch timestamp corruption
- Rapid artificial bursts
- Metadata sparsity
- Unnatural distribution patterns

Usage:
```
    python listenbrainz_audit_v2.py export.json
```
Optional:
```
    --near-window 60   # near duplicate window in seconds
```

## General Limitations Across All Scripts
- No canonical track identity resolution unless MBIDs are present.
- No cross-platform reconciliation beyond simple matching logic.
- Timestamp comparisons assume Unix epoch accuracy.
- Heuristic thresholds (5s, 10s, 60s, etc.) may need adjustment per dataset.
- These tools assist analysis but cannot guarantee absolute historical authenticity.
  
---
Note, these scripts were made with the help of ChatGPT. I don't know how to code python.
