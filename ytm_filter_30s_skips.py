import re
from datetime import datetime

# This is step 2.

INPUT_FILE = "music-and-topic-history.html"
OUTPUT_FILE = "music-30s-cleaned.html"
CLUSTER_WINDOW = 30

timestamp_pattern = re.compile(
    r'([A-Za-z]{3} \d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2} [AP]M [A-Z]+)'
)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    html = f.read()

entries = html.split('<div class="outer-cell')

parsed = []

for entry in entries:
    if "Watched" not in entry:
        continue

    entry = entry.replace("\u202f", " ")

    match = timestamp_pattern.search(entry)
    if not match:
        continue

    try:
        timestamp = datetime.strptime(
            match.group(1),
            "%b %d, %Y, %I:%M:%S %p %Z"
        )
        parsed.append((entry, timestamp))
    except:
        continue

# Sort chronologically (oldest → newest)
parsed.sort(key=lambda x: x[1])

clusters_kept = []
removed = 0

if parsed:
    cluster = [parsed[0]]

    for current in parsed[1:]:
        prev = cluster[-1]
        gap = (current[1] - prev[1]).total_seconds()

        if gap <= CLUSTER_WINDOW:
            cluster.append(current)
        else:
            # keep last item of finished cluster
            clusters_kept.append(cluster[-1])
            removed += len(cluster) - 1
            cluster = [current]

    # finalize last cluster
    clusters_kept.append(cluster[-1])
    removed += len(cluster) - 1

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("<html><body>\n")
    for entry, _ in clusters_kept:
        out.write('<div class="outer-cell' + entry)
    out.write("\n</body></html>")

print("\n===== 10s CLUSTER FILTER RESULTS =====")
print("Original entries: ", len(parsed))
print("Removed as skips:", removed)
print("Final entries:   ", len(clusters_kept))
print("=======================================")
print("Created:", OUTPUT_FILE)
