import os
from pymongo import MongoClient


# =========================
# MONGODB CONNECTION
# =========================

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set")


client = MongoClient(MONGO_URI)

db = client["casino_bot"]

users_collection = db["users"]


# =========================
# UNIQUE USER ID
# =========================

users_collection.create_index(
    "user_id",
    unique=True
)


# =========================
# GET USER
# =========================

def get_user(user):

    user_id = user.id

    existing = users_collection.find_one(
        {"user_id": user_id}
    )

    # User ရှိပြီးသား
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

        return users_collection.find_one(
            {"user_id": user_id}
        )

    # User အသစ်
    new_user = {
        "user_id": user_id,
        "name": user.first_name or "User",
        "username": user.username or "",
        "usd": 0,
        "dia": 0,
        "welcome_bonus": False
    }

    users_collection.insert_one(new_user)

    return users_collection.find_one(
        {"user_id": user_id}
    )


# =========================
# UPDATE BALANCE
# =========================

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


# =========================
# GET USER BY ID
# =========================

def get_user_by_id(user_id):

    return users_collection.find_one(
        {"user_id": user_id}
    )
