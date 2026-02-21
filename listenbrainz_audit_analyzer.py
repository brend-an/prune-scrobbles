#!/usr/bin/env python3

"""
ListenBrainz Export Audit Analyzer

This script analyzes a ListenBrainz export JSON file and generates
a comprehensive integrity report.

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
    python export_audit_analyzer.py export.json

Optional:
    --near-window 10   # near duplicate window in seconds
"""

import json
import argparse
from collections import Counter
from datetime import datetime, UTC
import math


# ----------------------------
# Helper Functions
# ----------------------------

def load_export(path):
    """Load ListenBrainz export JSON file."""
    with open(path) as f:
        return json.load(f)


def normalize_track_key(listen):
    """
    Create a normalized key for identifying duplicate tracks.
    Uses artist + track name + timestamp.
    """
    meta = listen.get("track_metadata", {})
    artist = meta.get("artist_name", "").strip().lower()
    track = meta.get("track_name", "").strip().lower()
    ts = listen.get("listened_at")

    return (artist, track, ts)


def get_year(ts):
    """Convert UNIX timestamp to year (UTC, timezone-aware)."""
    return datetime.fromtimestamp(ts, UTC).year


def shannon_entropy(counter):
    """Calculate Shannon entropy of a distribution."""
    total = sum(counter.values())
    entropy = 0

    for count in counter.values():
        p = count / total
        entropy -= p * math.log2(p)

    return entropy


# ----------------------------
# Main Analysis Function
# ----------------------------

def analyze(data, near_window=None):
    print("Running audit analysis...\n")

    total_listens = len(data)
    print(f"Total listens: {total_listens}")

    # ----------------------------
    # Exact Duplicate Detection
    # ----------------------------

    seen = set()
    duplicates = 0

    for listen in data:
        key = normalize_track_key(listen)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)

    print(f"Exact duplicates: {duplicates}")
    print(f"Unique track events: {total_listens - duplicates}\n")

    # ----------------------------
    # Artist Statistics
    # ----------------------------

    artist_counter = Counter()
    year_counter = Counter()
    durations = []
    timestamps = []

    for listen in data:
        meta = listen.get("track_metadata", {})
        artist = meta.get("artist_name")
        ts = listen.get("listened_at")

        if artist:
            artist_counter[artist] += 1

        if ts:
            year_counter[get_year(ts)] += 1
            timestamps.append(ts)

        # Duration metadata (if present)
        duration_ms = meta.get("additional_info", {}).get("duration_ms")
        if duration_ms:
            durations.append(duration_ms / 1000)  # convert to seconds

    print("Unique artists:", len(artist_counter))
    entropy = shannon_entropy(artist_counter)
    print("Artist entropy:", round(entropy, 4), "\n")

    # ----------------------------
    # Top Artists
    # ----------------------------

    print("Top 20 Artists:")
    for i, (artist, count) in enumerate(artist_counter.most_common(20), 1):
        print(f"{i:2d}. {artist} - {count}")
    print()

    # ----------------------------
    # Year Distribution
    # ----------------------------

    print("Year Distribution:")
    for year in sorted(year_counter):
        print(year, year_counter[year])
    print()

    # ----------------------------
    # Skip Analysis
    # ----------------------------

    skip_thresholds = [5, 10, 15, 30, 60, 90]
    skip_counts = {t: 0 for t in skip_thresholds}

    for d in durations:
        for threshold in skip_thresholds:
            if d <= threshold:
                skip_counts[threshold] += 1

    print("Skip Analysis (duration ≤ threshold):")
    for t in skip_thresholds:
        print(f"≤{t}s: {skip_counts[t]}")
    print()

    # ----------------------------
    # Duration Distribution
    # ----------------------------

    if durations:
        duration_buckets = Counter()

        for d in durations:
            if d <= 30:
                duration_buckets["≤30s"] += 1
            elif d <= 60:
                duration_buckets["31–60s"] += 1
            elif d <= 120:
                duration_buckets["61–120s"] += 1
            elif d <= 240:
                duration_buckets["121–240s"] += 1
            else:
                duration_buckets[">240s"] += 1

        print("Duration Distribution:")
        for bucket, count in duration_buckets.items():
            print(bucket, count)
        print()

    # ----------------------------
    # Rapid Burst Detection
    # ----------------------------

    if timestamps:
        timestamps.sort()
        rapid_5 = 0
        rapid_10 = 0

        for i in range(1, len(timestamps)):
            delta = timestamps[i] - timestamps[i - 1]
            if delta <= 5:
                rapid_5 += 1
            if delta <= 10:
                rapid_10 += 1

        print("Rapid Burst Detection:")
        print("≤5s gaps:", rapid_5)
        print("≤10s gaps:", rapid_10)
        print()

    # ----------------------------
    # Near Duplicate Detection
    # ----------------------------

    if near_window:
        print(f"Near duplicate detection (±{near_window}s window):")

        near_dupes = 0
        sorted_data = sorted(data, key=lambda x: x["listened_at"])

        for i in range(1, len(sorted_data)):
            curr = sorted_data[i]
            prev = sorted_data[i - 1]

            if abs(curr["listened_at"] - prev["listened_at"]) <= near_window:
                if normalize_track_key(curr)[:2] == normalize_track_key(prev)[:2]:
                    near_dupes += 1

        print("Near duplicates:", near_dupes)
        print()

    print("===== AUDIT COMPLETE =====")


# ----------------------------
# CLI Entry
# ----------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ListenBrainz Export Audit Analyzer")
    parser.add_argument("file", help="Path to ListenBrainz export JSON file")
    parser.add_argument("--near-window", type=int, help="Enable near duplicate detection with window (seconds)")

    args = parser.parse_args()

    data = load_export(args.file)
    analyze(data, args.near_window)
