import time
from app.core.reddit_client import reddit
from app.globals import TICKER_SET, SUPPORTED_SUBREDDITS, TICKER_PATTERN
from app.services.db_service import db
from app.services.state_service import load_last_seen, save_last_seen
from app.services.classification_service import get_sentiment

def fetch_recent_posts() -> None:
    last_seen = load_last_seen()

    for s in SUPPORTED_SUBREDDITS:
        subreddit_name = s[2:].lower()
        subreddit_collection = db[subreddit_name]
        count = 0
        added = 0
        updated = 0

        newest_post_time = None
        print_newest_post_time = None
        oldest_post_time = None
        print_oldest_post_time = None
        newest_post_id = None
        oldest_post_id = None

        last_seen_utc = last_seen.get(subreddit_name, 0)

        for post in reddit.subreddit(subreddit_name).new(limit=None):
            if post.created_utc <= last_seen_utc:
                print(f"[{subreddit_name}] Reached previously seen post {post.id}, breaking early.")
                break

            count += 1
            title_and_body = f"{post.title if post.title else ''} {post.selftext if post.selftext else ''}"
            title_ticker = TICKER_PATTERN.findall(post.title)
            mentioned_tickers = set([t for t in TICKER_PATTERN.findall(title_and_body) if t in TICKER_SET])
            
            if title_ticker and not post.stickied:
                ticker_sentiment = get_sentiment(title_and_body)
                if not newest_post_time:
                    newest_post_time = post.created_utc
                    newest_post_id = post.id
                if not oldest_post_time or post.created_utc < oldest_post_time:
                    oldest_post_time = post.created_utc
                    oldest_post_id = post.id
                doc = {
                    "id": post.id,
                    "title": post.title,
                    "body": post.selftext,
                    "created_utc": post.created_utc,
                    "author": str(post.author) if post.author else None,
                    "original_content": post.is_original_content,
                    "mentioned_tickers": list(mentioned_tickers),
                    "title_ticker": title_ticker,
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
        print(f"in subreddit {subreddit_name}, visited: {count}, added: {added}, updated: {updated} number of posts")
        print(f"oldest post created at {print_oldest_post_time} with ID {oldest_post_id}", f"newest post created at {print_newest_post_time} with ID {newest_post_id}")

        if newest_post_time:
            last_seen[subreddit_name] = max(
                last_seen.get(subreddit_name, 0),
                newest_post_time
            )

    save_last_seen(last_seen)
    
if __name__ == "__main__":
    print("\n=== Fetching Reddit posts ===")
    try:
        fetch_recent_posts()
    except Exception as e:
        print(f"Error during fetch cycle: {e}")
    print("Sleeping for 30 min...\n")

    


        


