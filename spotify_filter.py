import json

FILES = [
    "Streaming_History_Audio_2018-2020_0.json", # Change this file's name to the filename of your exported Spotify JSON file.
    "Streaming_History_Audio_2020-2024_1.json" # Change this file's name to the filename of your exported Spotify JSON file.
]

MIN_MS = 30000  # 30 seconds
# Change this duration to 5, 10, 15, 30, 45, or 60 seconds depending on how long you want scrobbles for skipped tracks.

all_entries = []

for file in FILES:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        all_entries.extend(data)

print(f"Total raw entries: {len(all_entries)}")

cleaned = []
removed_skips = 0
removed_podcasts = 0
removed_missing = 0

for entry in all_entries:
    # Remove podcasts
    if entry.get("episode_name") is not None:
        removed_podcasts += 1
        continue

    # Remove missing metadata
    if not entry.get("master_metadata_track_name") or not entry.get("master_metadata_album_artist_name"):
        removed_missing += 1
        continue

    # Remove skips
    if entry.get("ms_played", 0) < MIN_MS:
        removed_skips += 1
        continue

    cleaned.append(entry)

print("\n===== FILTER RESULTS =====")
print(f"Total original:      {len(all_entries)}")
print(f"Removed skips:       {removed_skips}")
print(f"Removed podcasts:    {removed_podcasts}")
print(f"Removed missing:     {removed_missing}")
print(f"Final clean entries: {len(cleaned)}")
print("==========================")

with open("spotify-cleaned.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2)

print("\nCreated: spotify-cleaned.json")
