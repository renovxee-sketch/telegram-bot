import os
import certifi
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set")


client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=30000
)

# MongoDB connection စစ်ရန်
client.admin.command("ping")


db = client["casino_bot"]
users_collection = db["users"]


users_collection.create_index(
    "user_id",
    unique=True
)


def get_user(user):
    user_id = user.id

    existing = users_collection.find_one({
        "user_id": user_id
    })

    if existing:
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "name": user.first_name or "User",
                    "username": user.username or ""
                }
            }
        )

        return users_collection.find_one({
            "user_id": user_id
        })

    new_user = {
        "user_id": user_id,
        "name": user.first_name or "User",
        "username": user.username or "",
        "usd": 0,
        "dia": 0,
        "welcome_bonus": False
    }

    try:
        users_collection.insert_one(new_user)
    except DuplicateKeyError:
        pass

    return users_collection.find_one({
        "user_id": user_id
    })


def update_balance(user_id, usd_change=0, dia_change=0):
    users_collection.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "usd": usd_change,
                "dia": dia_change
            }
        }
    )


def get_user_by_id(user_id):
    return users_collection.find_one({
        "user_id": user_id
    })
