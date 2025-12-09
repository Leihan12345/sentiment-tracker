from app.services.reddit_service_post import fetch_recent_posts
from app.services.reddit_service_comment import fetch_recent_comments

def main():
    fetch_recent_posts()
    fetch_recent_comments()

if __name__ == "__main__":
    main()