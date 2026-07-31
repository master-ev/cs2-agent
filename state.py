import json
import os

STATE_FILE = "seen.json"

def load_seen():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        print("Couldn't read the state file.")
        return {}

def save_seen(seen):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(seen, f, indent=2)
    except OSError:
        print("Couldn't write the state file.")

def get_seen_ids(seen, source):
    return seen.get(source, [])

def mark_as_seen(seen, source, item_id):
    if source not in seen:
        seen[source] = []
    if item_id not in seen[source]:
        seen[source].append(item_id)