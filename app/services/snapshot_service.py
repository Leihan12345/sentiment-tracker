import time
from datetime import datetime, UTC, timedelta
from app.services.db_service import client
from app.services.reddit_service import fetch_recent_posts

def snapshot_post_collection():
    src_db_name = "post_collection"
    today_str = datetime.now(UTC).strftime("%d_%m_%Y")
    dst_db_name = f"post_collection_{today_str}"

    src_db = client[src_db_name]
    dst_db = client[dst_db_name]

    for coll_name in src_db.list_collection_names():
        src_coll = src_db[coll_name]
        dst_coll = dst_db[coll_name]
        docs = list(src_coll.find())
        if docs:
            dst_coll.insert_many(docs)

def cleanup_old_snapshots(retention_days=7):
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    for db_name in client.list_database_names():
        if db_name.startswith("post_collection_"):
            try:
                date_str = db_name.replace("post_collection_", "")
                db_date = datetime.strptime(date_str, "%d_%m_%Y").replace(tzinfo=UTC)
                if db_date < cutoff:
                    client.drop_database(db_name)
                    print(f"Dropped old snapshot: {db_name}")
            except Exception:
                pass
            
snapshot_post_collection()

cleanup_old_snapshots()