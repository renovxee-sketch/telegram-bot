import os
import json
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN မတွေ့ပါ။")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

OWNER_USERNAME = "Ruifineshyt"
DATA_FILE = "bot_data.json"


# ==================================================
# DATA
# ==================================================

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass

    return {"users": {}}


data = load_data()
users = data.get("users", {})


def save_data():
    data["users"] = users

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

    if username:
        return username.lower() == OWNER_USERNAME.lower()

    return False


# ==================================================
# BOT MENU
# ==================================================

def set_commands():

    commands = [
        telebot.types.BotCommand("start", "Start Bot"),
        telebot.types.BotCommand("balance", "Check Balance"),
        telebot.types.BotCommand("game", "Game Menu"),
        telebot.types.BotCommand("usd", "Add USD"),
        telebot.types.BotCommand("dia", "Add Diamonds"),
        telebot.types.BotCommand("giftusd", "Gift USD")
    ]

    bot.set_my_commands(commands)


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
        f"💵 USD: <b>${user['usd']:,
