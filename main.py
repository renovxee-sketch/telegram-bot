import os
import random
import time
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# User balances
users = {}


@app.route("/")
def home():
    return "Game Bot is running!"


# ================= START =================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    # လူသစ်ဆိုရင်သာ USD 10000 ပေးမယ်
    if user_id not in users:
        users[user_id] = {
            "usd": 10000
        }

    usd_balance = users[user_id]["usd"]

    text = (
        f'👋 မင်္ဂလာပါ <a href="tg://user?id={user_id}">{user_name}</a>!\n\n'
        f'🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!\n\n'
        f'💵 USD Balance: ${usd_balance:,}\n\n'
        '👇 အောက်ပါ Button ကို နှိပ်ပြီး
