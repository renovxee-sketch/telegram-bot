import os
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN မတွေ့ပါ။ Render Environment Variables မှာ BOT_TOKEN ထည့်ပါ။")

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route("/")
def home():
    return "Game Bot is running!"


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    text = """
🎮 Ruifineshyt Game Bot

👋 မင်္ဂလာပါ!

🎲 Dice
🎳 Bowling
⚽ Football
🏀 Basketball
🎰 Slot
🎯 Dart

👥 သူငယ်ချင်းတွေနဲ့အတူ ကစားနိုင်ပါတယ်။

👇 Group ထဲထည့်ပြီး စတင်ကစားပါ။
"""

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "➕ Add Me Your GP",
            url="https://t.me/Ruifineshyt_bot?startgroup=true"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "🎮 Game Menu",
            callback_data="game_menu"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=keyboard
    )


# =========================
# GAME MENU
# =========================

@bot.message_handler(commands=["game"])
def game(message):

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("⚽ Football", callback_data="game_football"),
        InlineKeyboardButton("🎰 Slot", callback_data="game_slot"),
        InlineKeyboardButton("🎲 Dice", callback_data="game_dice"),
        InlineKeyboardButton("🎯 Dart", callback_data="game_dart"),
        InlineKeyboardButton("🎳 Bowling", callback_data="game_bowling"),
        InlineKeyboardButton("🏀 Basketball", callback_data="game_basketball")
    )

    bot.send_message(
        message.chat.id,
        "🎮 GAME MENU\n\nဂိမ်းတစ်ခုရွေးပါ 👇",
        reply_markup=keyboard
    )


# =========================
# GAME BUTTONS
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "game_menu")
def game_menu_button(call):

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("⚽ Football", callback_data="game_football"),
        InlineKeyboardButton("🎰 Slot", callback_data="game_slot"),
        InlineKeyboardButton("🎲 Dice", callback_data="game_dice"),
        InlineKeyboardButton("🎯 Dart", callback_data="game_dart"),
        InlineKeyboardButton("🎳 Bowling", callback_data="game_bowling"),
        InlineKeyboardButton("🏀 Basketball", callback_data="game_basketball")
    )

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "🎮 GAME MENU\n\nဂိမ်းတစ်ခုရွေးပါ 👇",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("game_"))
def game_button(call):

    game_name = call.data

    bot.answer_callback_query(call.id)

    if game_name == "game_dice":
        bot.send_dice(call.message.chat.id, emoji="🎲")

    elif game_name == "game_bowling":
        bot.send_dice(call.message.chat.id, emoji="🎳")

    elif game_name == "game_football":
        bot.send_dice(call.message.chat.id, emoji="⚽")

    elif game_name == "game_basketball":
        bot.send_dice(call.message.chat.id, emoji="🏀")

    elif game_name == "game_slot":
        bot.send_dice(call.message.chat.id, emoji="🎰")

    elif game_name == "game_dart":
        bot.send_dice(call.message.chat.id, emoji="🎯")


# =========================
# DIRECT COMMANDS
# =========================

@bot.message_handler(commands=["dice"])
def dice(message):
    bot.send_dice(message.chat.id, emoji="🎲")


@bot.message_handler(commands=["bowling"])
def bowling(message):
    bot.send_dice(message.chat.id, emoji="🎳")


@bot.message_handler(commands=["football"])
def football(message):
    bot.send_dice(message.chat.id, emoji="⚽")


@bot.message_handler(commands=["basketball"])
def basketball(message):
    bot.send_dice(message.chat.id, emoji="🏀")


@bot.message_handler(commands=["slot"])
def slot(message):
    bot.send_dice(message.chat.id, emoji="🎰")


@bot.message_handler(commands=["dart"])
def dart(message):
    bot.send_dice(message.chat.id, emoji="🎯")


# =========================
# FLASK SERVER
# =========================

def run():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )


# =========================
# START BOT
# =========================

Thread(target=run).start()

bot.infinity_polling()
