import os
import json
import telebot
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

OWNER_USERNAME = "Ruifineshyt"
DATA_FILE = "bot_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}


data = load_data()
users = data["users"]


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_user(user_id):
    user_id = str(user_id)

    if user_id not in users:
        users[user_id] = {
            "usd": 0,
            "dia": 0
        }
        save_data()

    return users[user_id]


def is_owner(message):
    username = message.from_user.username

    return username and username.lower() == OWNER_USERNAME.lower()


@app.route("/")
def home():
    return "Bot is running!"


# ==============================
# GIFT USD
# ==============================

@bot.message_handler(commands=["giftusd"])
def giftusd(message):

    if not is_owner(message):
        return

    if not message.reply_to_message:
        bot.reply_to(
            message,
            "❌ ပေးမယ့်သူရဲ့ Message ကို Reply လုပ်ပါ။"
        )
        return

    parts = message.text.split()

    if len(parts) != 2:
        bot.reply_to(
            message,
            "❌
