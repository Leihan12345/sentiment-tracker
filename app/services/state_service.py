import json, os

LAST_SEEN_PATH = "app/data/last_seen.json"

def load_last_seen():
    if os.path.exists(LAST_SEEN_PATH):
        with open(LAST_SEEN_PATH, "r") as f:
            return json.load(f)
    return {}

def save_last_seen(data):
    os.makedirs(os.path.dirname(LAST_SEEN_PATH), exist_ok=True)
    with open(LAST_SEEN_PATH, "w") as f:
        json.dump(data, f, indent=2)