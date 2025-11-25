from pymongo import MongoClient
from datetime import datetime, UTC
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "post_collection"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

last_seen_collection = db["last_seen"]