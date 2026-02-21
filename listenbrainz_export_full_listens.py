#!/usr/bin/env python3

"""
ListenBrainz Full Export Script

Exports all listens for a given user using the ListenBrainz API.
Supports automatic resume and safe incremental writes.

Usage:
    python listenbrainz_export_full_listens.py --username USER --token TOKEN

Optional:
    --output filename.json
"""

import requests
import json
import time
import os
import argparse
import sys

API = "https://api.listenbrainz.org/1"
BATCH_SIZE = 1000
SLEEP_BETWEEN_REQUESTS = 0.5
MAX_RETRIES = 5


def fetch_batch(username, token, max_ts=None):
    headers = {"Authorization": f"Token {token}"}
    params = {"count": BATCH_SIZE}

    if max_ts:
        params["max_ts"] = max_ts

    response = requests.get(
        f"{API}/user/{username}/listens",
        headers=headers,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def safe_write_json(path, data):
    temp_path = path + ".tmp"
    with open(temp_path, "w") as f:
        json.dump(data, f)
    os.replace(temp_path, path)


def main():
    parser = argparse.ArgumentParser(description="Export all ListenBrainz listens.")
    parser.add_argument("--username", required=True, help="ListenBrainz username")
    parser.add_argument("--token", required=True, help="ListenBrainz user token")
    parser.add_argument("--output", help="Output file name")

    args = parser.parse_args()

    username = args.username
    token = args.token
    output_file = args.output or f"{username}_full.json"

    all_listens = []
    max_ts = None

    # Resume support
    if os.path.exists(output_file):
        print("Resuming previous export...")
        with open(output_file) as f:
            all_listens = json.load(f)
        if all_listens:
            max_ts = min(l["listened_at"] for l in all_listens) - 1
            print(f"Resuming from timestamp: {max_ts}")

    while True:
        retries = 0

        while retries < MAX_RETRIES:
            try:
                data = fetch_batch(username, token, max_ts)
                break
            except Exception as e:
                retries += 1
                wait = 2 ** retries
                print(f"Error: {e}")
                print(f"Retrying in {wait}s ({retries}/{MAX_RETRIES})...")
                time.sleep(wait)

        if retries == MAX_RETRIES:
            print("Max retries exceeded. Exiting.")
            sys.exit(1)

        listens = data["payload"]["listens"]

        if not listens:
            break

        all_listens.extend(listens)
        max_ts = min(l["listened_at"] for l in listens) - 1

        print(f"Fetched total: {len(all_listens)} listens")

        safe_write_json(output_file, all_listens)

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print("Export complete.")
    print(f"Total listens exported: {len(all_listens)}")


if __name__ == "__main__":
    main()
