import os
import telebot
from flask import Flask
from threading import Thread

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==================================================
# BOT TOKEN
# ==================================================

TOKEN = os.getenv("BOT_TOKEN")

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
            "usd": 0,
            "dia": 0
        }

    return users[user_id]


# ==================================================
# HOME
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
        f'💎 Diamonds: {user["dia"]:,}\n'
        f'💵 USD: ${user["usd"]:,}\n\n'
        '👇 အောက်ပါ Button ကို နှိပ်ပြီး '
        'သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!'
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "➕ Add Me Your Group",
            url="https://t.me/Ruifineshyt_bot?startgroup=true"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# BALANCE
# ==================================================

@bot.message_handler(commands=["balance"])
def balance(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(user_id)

    text = (
        f"👤 <b>{user_name} ({user_id})</b> ၏ လက်ကျန်ငွေ\n"
        f"💎 Diamonds: <b>{user['dia']:,}</b>💎\n"
        f"💵 USD: <b>${user['usd']:,}USD</b>"
    )

    bot.reply_to(
        message,
        text,
        parse_mode="HTML"
    )


# ==================================================
# RENDER WEB SERVER
# ==================================================

def run():

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )


Thread(target=run).start()


# ==================================================
# START BOT
# ==================================================

print("Bot is starting...")

bot.infinity_polling()
