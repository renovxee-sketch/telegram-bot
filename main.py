import os
import json
import time
import random
import telebot

from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# =========================
# BOT SETTINGS
# =========================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN မတွေ့ပါ")

bot = telebot.TeleBot(TOKEN)

OWNER_USERNAME = "Ruifineshyt"

DATA_FILE = "bot_data.json"


# =========================
# DATA SYSTEM
# =========================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


data = load_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(user_id, first_name=None):
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "name": first_name or "User",
            "usd": 0,
            "dia": 0
        }
        save_data()

    if first_name:
        data[user_id]["name"] = first_name

    return data[user_id]


# =========================
# OWNER CHECK
# =========================

def is_owner(message):
    username = message.from_user.username

    if not username:
        return False

    return username.lower() == OWNER_USERNAME.lower()


# =========================
# BOT COMMANDS
# =========================

def set_commands():
    commands = [
        telebot.types.BotCommand("start", "Start Bot"),
        telebot.types.BotCommand("balance", "Check Balance"),
        telebot.types.BotCommand("game", "Game Center"),
        telebot.types.BotCommand("usd", "Add USD"),
        telebot.types.BotCommand("dia", "Add Diamonds"),
        telebot.types.BotCommand("giftusd", "Gift USD")
    ]

    bot.set_my_commands(commands)


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name
    )

    user_name = message.from_user.first_name
    user_id = message.from_user.id

    mention = (
        f'<a href="tg://user?id={user_id}">'
        f'{user_name}'
        f'</a>'
    )

    text = f"""
👋 မင်္ဂလာပါ {mention}!

🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!

💎 Diamonds: {user["dia"]:,}💎
💵 USD: ${user["usd"]:,}USD

👇 အောက်ပါ Button ကို နှိပ်ပြီး သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!
"""

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
        parse_mode="HTML",
        reply_markup=keyboard
    )


# =========================
# BALANCE
# =========================

@bot.message_handler(commands=["balance"])
def balance(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name
    )

    name = message.from_user.first_name
    user_id = message.from_user.id

    text = f"""
👤 {name} ({user_id}) ၏ လက်ကျန်ငွေ

💎 Diamonds: {user["dia"]:,}💎
💵 USD: ${user["usd"]:,}USD
"""

    bot.reply_to(message, text)


# =========================
# GAME CENTER
# =========================

@bot.message_handler(commands=["game"])
def game(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name
    )

    user_name = message.from_user.first_name
    user_id = message.from_user.id

    mention = (
        f'<a href="tg://user?id={user_id}">'
        f'{user_name}'
        f'</a>'
    )

    text = f"""
╔════════════════════════╗
🎮 GAME CENTER 🎮
╚════════════════════════╝

👤 {mention}

━━━━━━━━━━━━━━━━━━━━━━

🎰 ဂိမ်းကမ္ဘာမှ ကြိုဆိုပါတယ်!

ဒီနေရာမှာ သင့်ကံကို စမ်းသပ်ပြီး 🎯
စိတ်လှုပ်ရှားဖွယ် Game များကို
အပျော်တမ်း ကစားနိုင်ပါတယ်! 🔥

━━━━━━━━━━━━━━━━━━━━━━

💰 သင့်လက်ရှိ Balance

💵 USD ┃ ${user["usd"]:,}
💎 DIA ┃ {user["dia"]:,}

━━━━━━━━━━━━━━━━━━━━━━

🎮 လက်ရှိ ကစားနိုင်သော Game

🎰 SLOT MACHINE
└ 🍒 🍋 🍇 7️⃣ BAR
└ သင့်ကံကို စမ်းသပ်လိုက်ပါ! 🍀

👇 အောက်က Game ကိုရွေးပြီး စတင်ကစားပါ!
"""

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "🎰 SLOT MACHINE 🎰",
            callback_data="game_slot"
        )
    )

    bot.reply_to(
        message,
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


# =========================
# SLOT BET BUTTONS
# =========================

def slot_bet_keyboard():

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton("💵 10 USD", callback_data="slot_bet_10"),
        InlineKeyboardButton("💵 100 USD", callback_data="slot_bet_100")
    )

    keyboard.row(
        InlineKeyboardButton("💵 1K USD", callback_data="slot_bet_1000"),
        InlineKeyboardButton("💵 10K USD", callback_data="slot_bet_10000")
    )

    keyboard.row(
        InlineKeyboardButton("💵 100K USD", callback_data="slot_bet_100000"),
        InlineKeyboardButton("💵 300K USD", callback_data="slot_bet_300000")
    )

    keyboard.row(
        InlineKeyboardButton("💵 500K USD", callback_data="slot_bet_500000"),
        InlineKeyboardButton("💵 1M USD", callback_data="slot_bet_1000000")
    )

    return keyboard


# =========================
# SLOT GAME
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "game_slot")
def game_slot(call):

    user = get_user(
        call.from_user.id,
        call.from_user.first_name
    )

    text = f"""
🎰 SLOT MACHINE 🎰

👤 {call.from_user.first_name}

💵 Balance: ${user["usd"]:,}

👇 လောင်းကြေးရွေးပါ
"""

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=slot_bet_keyboard()
    )

    bot.answer_callback_query(call.id)


# =========================
# SLOT BET
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("slot_bet_"))
def slot_bet(call):

    bet = int(call.data.replace("slot_bet_", ""))

    user = get_user(
        call.from_user.id,
        call.from_user.first_name
    )

    balance = int(user.get("usd", 0))

    # Balance မလောက်ရင်
    if balance < bet:

        bot.answer_callback_query(
            call.id,
            "❌ လောင်းကြေး မလောက်ပါ!",
            show_alert=True
        )

        return

    # =========================
    # BET ဖြတ်ခြင်း
    # =========================

    user["usd"] -= bet

    save_data()

    bot.answer_callback_query(call.id)

    # =========================
    # TELEGRAM REAL SLOT
    # =========================

    dice_message = bot.send_dice(
        call.message.chat.id,
        emoji="🎰"
    )

    # Telegram animation ပြီးအောင် စောင့်
    time.sleep(4)

    # =========================
    # RESULT
    # =========================

    dice_value = dice_message.dice.value

    # Telegram slot result value
    if dice_value in [1, 22, 43, 64]:

        result = "🎉 JACKPOT! နိုင်ပါတယ်! 🔥"

    elif dice_value in [16, 32, 48, 63]:

        result = "🎉 နိုင်ပါတယ်! 🍀"

    else:

        result = "😢 ရှုံးသွားပါတယ်။ နောက်တစ်ကြိမ် ကံကောင်းပါစေ! 🍀"

    # =========================
    # NEW RESULT MESSAGE
    # =========================

    result_text = f"""
🎰 SLOT RESULT 🎰

👤 {call.from_user.first_name}

{result}

💰 လက်ရှိ Balance
💵 ${user["usd"]:,} USD
💎 {user["dia"]:,} DIA
"""

    bot.send_message(
        call.message.chat.id,
        result_text
    )


# =========================
# OWNER USD
# =========================

@bot.message_handler(commands=["usd"])
def add_usd(message):

    if not is_owner(message):
        return

    parts = message.text.split()

    if len(parts) < 2:
        bot.reply_to(
            message,
            "အသုံးပြုပုံ:\n/usd 1000"
        )
        return

    try:
        amount = int(parts[1])
    except:
        bot.reply_to(
            message,
            "❌ Amount မှားနေပါတယ်!"
        )
        return

    if amount <= 0:
        bot.reply_to(
            message,
            "❌ Amount မှားနေပါတယ်
