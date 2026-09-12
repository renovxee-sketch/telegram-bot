import os
import json
import asyncio

BALANCES_FILE = "user_balances.json"
CARDS_FILE = "cards.json"
STATS_FILE = "game_stats.json"

OWNER_ID = int(os.getenv("OWNER_ID", "8032394583"))
balance_lock = asyncio.Lock()

# --- BALANCES ---
def load_balances():
    if os.path.exists(BALANCES_FILE):
        try:
            with open(BALANCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                converted = {}
                for k, v in data.items():
                    uid = int(k)
                    converted[uid] = {
                        "diamonds": v.get("diamonds", 5000000000 if uid == OWNER_ID else 500),
                        "usd": v.get("usd", 1000000 if uid == OWNER_ID else 10000)
                    }
                if OWNER_ID not in converted:
                    converted[OWNER_ID] = {"diamonds": 5000000000, "usd": 1000000}
                return converted
        except Exception as e:
            print(f"⚠️ Balance ဖတ်ရာတွင် အမှားရှိသည်: {e}")
    return {OWNER_ID: {"diamonds": 5000000000, "usd": 1000000}}

user_balances = load_balances()

def save_balances():
    try:
        temp_file = f"{BALANCES_FILE}.tmp"
        serializable_data = {str(k): v for k, v in user_balances.items()}
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)
        if os.path.exists(BALANCES_FILE):
            os.remove(BALANCES_FILE)
        os.rename(temp_file, BALANCES_FILE)
    except Exception as e:
        print(f"❌ Balance သိမ်းရာတွင် အမှားရှိသည်: {e}")

def get_user_data(user_id: int):
    user_id = int(user_id)
    if user_id not in user_balances:
        if user_id == OWNER_ID:
            user_balances[user_id] = {"diamonds": 5000000000, "usd": 1000000}
        else:
            user_balances[user_id] = {"diamonds": 500, "usd": 10000}
        save_balances()
    return user_balances[user_id]

# --- STATS ---
def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except Exception as e:
            print(f"⚠️ Stats ဖတ်ရာတွင် အမှားရှိသည်: {e}")
    return {}

rps_stats = load_stats()

def save_stats():
    try:
        temp_file = f"{STATS_FILE}.tmp"
        serializable_data = {str(k): v for k, v in rps_stats.items()}
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)
        if os.path.exists(STATS_FILE):
            os.remove(STATS_FILE)
        os.rename(temp_file, STATS_FILE)
    except Exception as e:
        print(f"❌ Stats သိမ်းရာတွင် အမှားရှိသည်: {e}")

# --- CARDS ---
def load_cards():
    if os.path.exists(CARDS_FILE):
        try:
            with open(CARDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Cards ဖတ်ရာတွင် အမှားရှိသည်: {e}")
            return []
    return []

bot_cards = load_cards()

def save_cards():
    try:
        temp_file = f"{CARDS_FILE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(bot_cards, f, ensure_ascii=False, indent=4)
        if os.path.exists(CARDS_FILE):
            os.remove(CARDS_FILE)
        os.rename(temp_file, CARDS_FILE)
    except Exception as e:
        print(f"❌ Cards သိမ်းရာတွင် အမှားရှိသည်: {e}")

