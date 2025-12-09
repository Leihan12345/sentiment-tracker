from datetime import datetime, timezone, timedelta
from app.core.reddit_client import reddit
from app.globals import SUPPORTED_SUBREDDITS
from app.services.db_service import db
from app.services.state_service import load_last_seen, save_last_seen
from app.services.classification_service import get_sentiment
from app.helper.ticker_helpers import find_comment_tickers


def fetch_recent_comments():

    cutoff_utc = (datetime.now(timezone.utc) - timedelta(days=2)).timestamp()

    for s in SUPPORTED_SUBREDDITS:
        subreddit_name = s[2:].lower()
        subreddit_collection = db[subreddit_name + "_comments"]
        
        print(f"\n=== Fetching comments for r/{subreddit_name} ===")

        for comment in reddit.subreddit(subreddit_name).comments(limit=None):
            if subreddit_collection.find_one({"id": comment.id}):
                print(f"[{subreddit_name}] Reached previously seen comment {comment.id}, breaking early.")
                break

            if comment.created_utc < cutoff_utc:
                break

            explicit_tickers = find_comment_tickers(comment.body)

            post_id = comment.link_id[3:]
            post_doc = db[subreddit_name].find_one({"id": post_id})
            post_ticker = post_doc.get("ticker") if post_doc else None

            main_ticker = None

            if explicit_tickers:
                if post_ticker:
                    if post_ticker in explicit_tickers:
                        main_ticker = post_ticker
                    else:
                        if len(explicit_tickers) == 1:
                            main_ticker = next(iter(explicit_tickers))
                else:
                    if len(explicit_tickers) == 1:
                        main_ticker = next(iter(explicit_tickers))
            else:
                if post_ticker:
                    bare = post_ticker[1:] if post_ticker.startswith("$") else post_ticker
                    if bare in comment.body:
                        main_ticker = post_ticker

            if main_ticker is not None:
                polarity_score = None
                try:
                    polarity_score = get_sentiment(comment.body)
                except Exception as e:
                    print(f"Error getting sentiment for comment {comment.id}: {e}")

                created_at_utc = datetime.fromtimestamp(
                    comment.created_utc, tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S")

                doc = {
                    "id": comment.id,
                    "body": comment.body,
                    "created_utc": comment.created_utc,
                    "created_at_utc": created_at_utc,
                    "ticker": main_ticker,
                    "polarity_score": polarity_score,
                }

                try:
                    subreddit_collection.update_one(
                        {"id": comment.id},
                        {"$set": doc},
                        upsert=True
                    )
                except Exception as e:
                    print(f"Error saving comment {comment.id}: {e}")


if __name__ == "__main__":
    fetch_recent_comments()
