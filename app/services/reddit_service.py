import time
from app.core.reddit_client import reddit
from app.globals import SUPPORTED_SUBREDDITS
from app.services.db_service import db
from app.services.state_service import load_last_seen, save_last_seen
from app.services.classification_service import get_sentiment
from app.helper.ticker_helpers import choose_main_ticker

def fetch_recent_posts() -> None:
    last_seen = load_last_seen()

    for s in SUPPORTED_SUBREDDITS:
        subreddit_name = s[2:].lower()
        subreddit_collection = db[subreddit_name]
        count = 0
        added = 0
        updated = 0

        newest_post_time = None
        oldest_post_time = None

        last_seen_utc = last_seen.get(subreddit_name, 0)

        for post in reddit.subreddit(subreddit_name).new(limit=None):
            if post.created_utc <= last_seen_utc:
                print(f"[{subreddit_name}] Reached previously seen post {post.id}, breaking early.")
                break

            count += 1
            title = f"{post.title if post.title else ''}"
            body = f"{post.selftext if post.selftext else ''}"

            main_ticker = choose_main_ticker(title, body)
            
            if main_ticker and not post.stickied:
                ticker_sentiment = get_sentiment(title + " " + body)
                if not newest_post_time:
                    newest_post_time = post.created_utc
                if not oldest_post_time or post.created_utc < oldest_post_time:
                    oldest_post_time = post.created_utc
                doc = {
                    "id": post.id,
                    "title": post.title,
                    "body": post.selftext,
                    "created_utc": post.created_utc,
                    "author": str(post.author) if post.author else None,
                    "original_content": post.is_original_content,
                    "ticker": main_ticker,
                    "polarity_score": ticker_sentiment
                }

                try:
                    result = subreddit_collection.update_one(
                        {"id": post.id},
                        {"$set": doc},
                        upsert=True
                    )
                    if result.modified_count > 0:
                        updated += 1
                    elif result.upserted_id is not None:
                        added += 1
                except Exception as e:
                    print(f"Error saving post {post.id}: {e}")

        if newest_post_time:
            last_seen[subreddit_name] = max(
                last_seen.get(subreddit_name, 0),
                newest_post_time
            )
        print(added, updated, count)

    save_last_seen(last_seen)
    
if __name__ == "__main__":
    print("\n=== Fetching Reddit posts ===")
    try:
        fetch_recent_posts()
    except Exception as e:
        print(f"Error during fetch cycle: {e}")

    


        


