#!/usr/bin/env python3

"""
ListenBrainz Audit Analyzer v2 (Forensic Mode)

This script performs deep integrity analysis on a ListenBrainz export JSON.

It evaluates:

STRUCTURAL INTEGRITY
- Total listens
- Exact duplicates
- Near duplicates (optional window)
- Timestamp collisions

TEMPORAL ANALYSIS
- Rapid burst detection (≤5s, ≤10s)
- Same-track rapid repeats
- Minimum/median gap

METADATA HEALTH
- Recording MBID coverage
- Duration metadata coverage
- Submission client breakdown

DIVERSITY ANALYSIS
- Unique artists
- Shannon entropy
- Yearly distribution
- Entropy by year

Usage:
    python listenbrainz_audit_v2.py export.json --near-window 60
"""

import json
import argparse
from collections import Counter, defaultdict
from datetime import datetime, UTC
import statistics
import math


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def load_export(path):
    with open(path) as f:
        return json.load(f)


def normalize_track(listen):
    meta = listen.get("track_metadata", {})
    artist = meta.get("artist_name", "").strip().lower()
    track = meta.get("track_name", "").strip().lower()
    return artist, track


def normalize_full_key(listen):
    artist, track = normalize_track(listen)
    ts = listen.get("listened_at")
    return artist, track, ts


def get_year(ts):
    return datetime.fromtimestamp(ts, UTC).year


def shannon_entropy(counter):
    total = sum(counter.values())
    entropy = 0
    for count in counter.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


# --------------------------------------------------
# Main Analysis
# --------------------------------------------------

def analyze(data, near_window=None):

    print("\n==============================")
    print("LISTENBRAINZ FORENSIC AUDIT v2")
    print("==============================\n")

    total = len(data)
    print("==== STRUCTURAL INTEGRITY ====")
    print("Total listens:", total)

    # Exact duplicates
    seen = set()
    exact_dupes = 0
    for l in data:
        key = normalize_full_key(l)
        if key in seen:
            exact_dupes += 1
        else:
            seen.add(key)

    print("Exact duplicates:", exact_dupes)

    # Timestamp collisions
    ts_counter = Counter(l["listened_at"] for l in data)
    collision_groups = {ts: c for ts, c in ts_counter.items() if c > 1}

    print("Timestamp collision groups:", len(collision_groups))
    if collision_groups:
        print("Largest collision:", max(collision_groups.values()))

    # Near duplicates
    near_dupes = 0
    if near_window:
        sorted_data = sorted(data, key=lambda x: x["listened_at"])
        for i in range(1, len(sorted_data)):
            curr = sorted_data[i]
            prev = sorted_data[i - 1]
            if abs(curr["listened_at"] - prev["listened_at"]) <= near_window:
                if normalize_track(curr) == normalize_track(prev):
                    near_dupes += 1
        print(f"Near duplicates (±{near_window}s):", near_dupes)

    print()

    # --------------------------------------------------
    print("==== TEMPORAL ANALYSIS ====")

    timestamps = sorted(l["listened_at"] for l in data)

    gaps = []
    rapid_5 = 0
    rapid_10 = 0

    for i in range(1, len(timestamps)):
        delta = timestamps[i] - timestamps[i - 1]
        gaps.append(delta)
        if delta <= 5:
            rapid_5 += 1
        if delta <= 10:
            rapid_10 += 1

    print("Rapid ≤5s:", rapid_5)
    print("Rapid ≤10s:", rapid_10)

    if gaps:
        print("Minimum gap:", min(gaps))
        print("Median gap:", int(statistics.median(gaps)))

    # Same-track rapid repeats
    same_track_15 = 0
    same_track_60 = 0

    sorted_data = sorted(data, key=lambda x: x["listened_at"])

    for i in range(1, len(sorted_data)):
        curr = sorted_data[i]
        prev = sorted_data[i - 1]
        delta = curr["listened_at"] - prev["listened_at"]

        if normalize_track(curr) == normalize_track(prev):
            if delta <= 15:
                same_track_15 += 1
            if delta <= 60:
                same_track_60 += 1

    print("Same track ≤15s:", same_track_15)
    print("Same track ≤60s:", same_track_60)
    print()

    # --------------------------------------------------
    print("==== METADATA HEALTH ====")

    mbid_count = 0
    duration_count = 0
    client_counter = Counter()

    for l in data:
        meta = l.get("track_metadata", {})
        add = meta.get("additional_info", {})

        if add.get("recording_mbid"):
            mbid_count += 1

        if add.get("duration_ms"):
            duration_count += 1

        client = add.get("submission_client")
        if client:
            client_counter[client] += 1
        else:
            client_counter["None"] += 1

    print("Recording MBID coverage:", f"{mbid_count}/{total}")
    print("Duration metadata coverage:", f"{duration_count}/{total}")
    print("\nSubmission Clients:")
    for client, count in client_counter.most_common():
        print(f"{client}: {count}")

    print()

    # --------------------------------------------------
    print("==== DIVERSITY ANALYSIS ====")

    artist_counter = Counter()
    year_counter = Counter()
    entropy_by_year = defaultdict(Counter)

    for l in data:
        artist = l.get("track_metadata", {}).get("artist_name")
        ts = l.get("listened_at")

        if artist:
            artist_counter[artist] += 1

        if ts:
            year = get_year(ts)
            year_counter[year] += 1
            if artist:
                entropy_by_year[year][artist] += 1

    print("Unique artists:", len(artist_counter))
    print("Global entropy:", round(shannon_entropy(artist_counter), 4))

    print("\nYearly distribution:")
    for year in sorted(year_counter):
        print(year, year_counter[year])

    print("\nEntropy by year:")
    for year in sorted(entropy_by_year):
        ent = shannon_entropy(entropy_by_year[year])
        print(year, round(ent, 3))

    print()

    # --------------------------------------------------
    # Integrity Score (simple heuristic)
    # --------------------------------------------------

    score = 100

    if exact_dupes > 0:
        score -= min(20, exact_dupes // 50)

    if rapid_5 > total * 0.05:
        score -= 10

    if len(collision_groups) > 10:
        score -= 10

    print("==== FINAL INTEGRITY SCORE ====")
    print("Integrity Score:", score, "/ 100")

    if score >= 90:
        print("Risk Level: LOW")
    elif score >= 75:
        print("Risk Level: MODERATE")
    else:
        print("Risk Level: HIGH")

    print("\n===== AUDIT COMPLETE =====\n")


# --------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ListenBrainz Forensic Audit v2")
    parser.add_argument("file", help="Path to export JSON")
    parser.add_argument("--near-window", type=int, help="Enable near duplicate window (seconds)")
    args = parser.parse_args()

    data = load_export(args.file)
    analyze(data, args.near_window)
