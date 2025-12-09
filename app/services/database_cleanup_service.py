import time

from app.globals import SUPPORTED_SUBREDDITS
from app.services.db_service import db

POST_RETENTION_SECONDS = 7 * 24 * 60 * 60      # 7 days
COMMENT_RETENTION_SECONDS = 24 * 60 * 60   # 1 day


def cleanup_old_docs() -> None:
    now = time.time()
    post_cutoff = now - POST_RETENTION_SECONDS
    comment_cutoff = now - COMMENT_RETENTION_SECONDS

    for s in SUPPORTED_SUBREDDITS:
        subreddit_name = s[2:].lower()
        posts_coll = db[subreddit_name]
        comments_coll = db[subreddit_name + "_comments"]

        posts_coll.delete_many({"created_utc": {"$lt": post_cutoff}})
        comments_coll.delete_many({"created_utc": {"$lt": comment_cutoff}})


if __name__ == "__main__":
    cleanup_old_docs()
