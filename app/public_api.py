from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import time

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["post_collection"]

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/posts/{subreddit}")
def get_wallstreetbets_posts(subreddit:str):
    collection = db[subreddit]
    posts = list(collection.find().sort("created_utc", -1))
    current_epoch_time = time.time()
    one_week_window = current_epoch_time - 592200
    display = []
    for p in posts:
        # if p["created_utc"] < one_week_window:
        #     break
        display.append(p)
    return [serialize_doc(d) for d in display]
