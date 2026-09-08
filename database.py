import os
import certifi
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set")

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=30000
)

# Connection စစ်ရန်
client.admin.command("ping")

db = client["casino_bot"]
users_collection = db["users"]

users_collection.create_index("user_id", unique=True)
