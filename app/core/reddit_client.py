import praw
import os
from dotenv import load_dotenv

load_dotenv()

def get_reddit_client() -> praw.reddit:
    return praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        user_agent=os.getenv("USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD")
    )

reddit = get_reddit_client()