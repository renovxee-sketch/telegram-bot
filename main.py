import os
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

# ==================================================
# OWNER ID
# ==================================================

# ဒီနေရာမှာ သင့် Telegram ID ထည့်ပါ
OWNER_ID = 123456789

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN မတွေ့ပါ။ Render Environment Variables မှာ BOT_TOKEN ထည့်ပါ။"
    )

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ==================================================
# USER DATA
# ==================================================

users = {}


def get_user(user_id):

    if user_id not in users:
        users[user_id] = {
            "usd": 10000,
            "dia": 0
        }

    return users[user_id]


# ==================================================
# WEB SERVER
# ==================================================

@app.route("/")
def home():
    return "Game Bot is running!"


# ==================================================
# START
# ==================================================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(user_id)

    text = (
        f'👋 မင်္ဂလာပါ '
        f'<a href="tg://user?id={user_id}">{user_name}</a>!\n\n'
        '🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!\n\n'
        f'💵 USD: ${user["usd"]:,}\n'
        f'💎 Diamond: {user["dia"]:,}\n\n'
        '👇 အောက်ပါ Button ကို နှိပ်ပြီး '
        'သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!'
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "➕ Add Me Your GP",
