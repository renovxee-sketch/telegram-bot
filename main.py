import os
import random
import time
import html
import telebot

from flask import Flask
from threading import Thread
from pymongo import MongoClient
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==================================================
# CONFIG
# ==================================================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB", "telegram_game_bot")

OWNER_USERNAME = "Ruifineshyt"

if not TOKEN:
    raise RuntimeError("BOT_TOKEN မတွေ့ပါ။")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI မတွေ့ပါ။")


bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# ==================================================
# MONGODB
# ==================================================

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db["users"]


def get_user(user_id, first_name=None):

    user_id = int(user_id)

    user = users_collection.find_one({
        "_id": user_id
    })

    if not user:

        user = {
            "_id": user_id,
            "usd": 0,
            "dia": 0,
            "name": first_name or "Player"
        }

        users_collection.insert_one(user)

    else:

        if first_name:
            users_collection.update_one(
                {"_id": user_id},
                {"$set": {"name": first_name}}
            )

    return users_collection.find_one({
        "_id": user_id
    })


def update_balance(user_id, usd_change=0, dia_change=0):

    users_collection.update_one(
        {"_id": int(user_id)},
        {
            "$inc": {
                "usd": usd_change,
                "dia": dia_change
            }
        },
        upsert=True
    )


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

        telebot.types.BotCommand(
            "start",
            "Start Bot"
        ),

        telebot.types.BotCommand(
            "balance",
            "Check Balance"
        ),

        telebot.types.BotCommand(
            "game",
            "Game Menu"
        ),

        telebot.types.BotCommand(
            "usd",
            "Add USD"
        ),

        telebot.types.BotCommand(
            "dia",
            "Add Diamonds"
        ),

        telebot.types.BotCommand(
            "giftusd",
            "Gift USD"
        ),

        telebot.types.BotCommand(
            "giftdia",
            "Gift Diamonds"
        )
    ]

    bot.set_my_commands(commands)


# ==================================================
# START
# ==================================================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(
        user_id,
        user_name
    )

    safe_name = html.escape(user_name)

    text = (
        f'👋 မင်္ဂလာပါ '
        f'<a href="tg://user?id={user_id}">{safe_name}</a>!\n\n'
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

    user = get_user(
        user_id,
        user_name
    )

    safe_name = html.escape(user_name)

    text = (
        f"👤 <b>{safe_name} ({user_id})</b> ၏ လက်ကျန်ငွေ\n"
        f"💎 Diamonds: <b>{user['dia']:,}</b>💎\n"
        f"💵 USD: <b>${user['usd']:,}USD</b>"
    )

    bot.reply_to(
        message,
        text,
        parse_mode="HTML"
    )


# ==================================================
# GAME MENU
# ==================================================

@bot.message_handler(commands=["game"])
def game(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    safe_name = html.escape(user_name)

    text = (
        f'👋 <a href="tg://user?id={user_id}">{safe_name}</a> ရေ!\n\n'
        '🎮 <b>ဆော့ကစားနိုင်သောဂိမ်းများ</b>\n\n'
        '🎰 <b>SLOT MACHINE</b>\n'
        '💵 လောင်းကြေးရွေးပြီး ကစားနိုင်ပါတယ်။'
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "🎰 Slot",
            callback_data="slot_menu"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# SLOT MENU
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "slot_menu"
)
def slot_menu(call):

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "💵 10",
            callback_data="bet_10"
        ),
        InlineKeyboardButton(
            "💵 100",
            callback_data="bet_100"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            "💵 1K",
            callback_data="bet_1000"
        ),
        InlineKeyboardButton(
            "💵 10K",
            callback_data="bet_10000"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            "💵 100K",
            callback_data="bet_100000"
        ),
        InlineKeyboardButton(
            "💵 300K",
            callback_data="bet_300000"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            "💵 500K",
            callback_data="bet_500000"
        ),
        InlineKeyboardButton(
            "💵 1M",
            callback_data="bet_1000000"
        )
    )

    bot.answer_callback_query(
        call.id
    )

    bot.edit_message_text(
        "🎰 <b>SLOT MACHINE</b>\n\n"
        "💵 လောင်းကြေးပမာဏကို ရွေးပါ။",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# SLOT SYMBOLS
# ==================================================

SLOT_SYMBOLS = [
    "🍒",
    "🍋",
    "🍊",
    "🍉",
    "🍇",
    "🥝",
    "🔔",
    "⭐",
    "BAR",
    "7"
]


# ==================================================
# SLOT RESULT
# ==================================================

def get_slot_result():

    # 777 = 30x
    if random.random() < 0.01:
        return ["7", "7", "7"], 30

    # BAR BAR BAR = 10x
    if random.random() < 0.02:
        return ["BAR", "BAR", "BAR"], 10

    # 77🍇 / 🍇77 = 3x
    if random.random() < 0.04:

        if random.choice([True, False]):
            return ["7", "7", "🍇"], 3

        return ["🍇", "7", "7"], 3

    # Other fruit x3 = 5x
    if random.random() < 0.08:

        fruit = random.choice([
            "🍒",
            "🍋",
            "🍊",
            "🍉",
            "🍇",
           
