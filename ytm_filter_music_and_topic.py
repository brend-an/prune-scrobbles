import re

# This is step 1.

INPUT_FILE = "watch-history.html" # import your Google Takeout YouTube watch history, put the file path here.
OUTPUT_FILE = "music-and-topic-history.html" # name your output file here.

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    html = f.read()

# Split into entries
entries = html.split('<div class="outer-cell')

kept = []
scanned = 0

for entry in entries:
    scanned += 1

    # Must contain Watched (ignore Viewed posts etc)
    if "Watched" not in entry:
        continue

    # Keep if:
    # 1) It is YouTube Music section
    # OR
    # 2) Channel name contains "- Topic"
    if (
        "YouTube Music" in entry
        or "- Topic</a>" in entry
    ):
        kept.append(entry)

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("<html><body>\n")
    for entry in kept:
        out.write('<div class="outer-cell' + entry)
    out.write("\n</body></html>")

print("\n===== EXTRACTION RESULTS =====")
print("Total scanned entries:", scanned)
print("Music + Topic kept:", len(kept))
print("==============================")
print("Created: music-and-topic-history.html")
