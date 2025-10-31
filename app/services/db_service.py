from pymongo import MongoClient
from datetime import datetime, UTC
import os
from dotenv import load_dotenv

load_dotenv()

def get_daily_db_name():
    today_str = datetime.now(UTC).strftime("%d_%m_%y")
    return f"post_collection_{today_str}"

MONGO_URI = os.getenv("MONGODB_URI")
DAILY_DB_NAME = get_daily_db_name()
DB_NAME = "post_collection"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
posts_collection = db["posts"]
posts_collection.create_index("last_updated", expireAfterSeconds=86400)
posts_collection.create_index("id", unique=True)