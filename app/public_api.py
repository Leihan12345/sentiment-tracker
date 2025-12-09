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
def get_posts(subreddit:str):
    collection = db[subreddit]
    posts = list(collection.find().sort("created_utc", -1))
    display = []
    for p in posts:
        display.append(p)
    return [serialize_doc(d) for d in display]

@app.get("/comments/{subreddit}")
def get_comments(subreddit:str):
    collection = db[subreddit + "_comments"]
    comments = list(collection.find().sort("created_utc", -1))
    display = []
    for comment in comments:
        display.append(comment)
    return [serialize_doc(d) for d in display]
