from app.services.db_service import db
from app.globals import SUPPORTED_SUBREDDITS

def load_last_seen():
    last_seen_dictionary = {}

    for doc in db["last_seen"].find():
        subreddit = doc["_id"]
        previous_timestamp = doc["last_seen_utc"]
        if doc["_id"] not in last_seen_dictionary:
            last_seen_dictionary[subreddit] = previous_timestamp

    if not last_seen_dictionary:
        # choose your default – 0 means "start from the beginning"
        default_ts = 0.0  # or time.time() if you want "start from now"

        bulk_docs = []
        for sr in SUPPORTED_SUBREDDITS:
            subreddit = sr[2:].lower()   # e.g. "r/stocks" -> "stocks"
            last_seen_dictionary[subreddit] = default_ts
            bulk_docs.append({
                "_id": subreddit,
                "last_seen_utc": default_ts,
            })

        if bulk_docs:
            db["last_seen"].insert_many(bulk_docs)
    return last_seen_dictionary

def save_last_seen(data):
    for subreddit, ts in data.items():
        db["last_seen"].update_one(
            {"_id": subreddit},
            {"$set": {"last_seen_utc": ts}},
            upsert=True,
        )