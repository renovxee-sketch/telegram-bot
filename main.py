import os
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("BOT_TOKEN not found!")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
    return "Game Bot is running!"


# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):

    user_name = message.from_user.first_name or "Player"
    user_id = message.from_user.id

    text = (
        f'👋 မင်္ဂလာပါ <a href="tg://user?id={user_id}">{user_name}</a>!\n\n'
        '🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!\n\n'
        '👇 အောက်ပါ Button ကို နှိပ်ပြီး သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!'
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "➕ Add Me Your GP",
            url="https://t.me/Ruifineshyt_bot?startgroup=true"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ================= GAME MENU =================
@bot.message_handler(commands=["game"])
def game_menu(message):

    keyboard = InlineKeyboardMarkup(row_width=2)

    buttons = [
        InlineKeyboardButton("⚽ Football", callback_data="football"),
        InlineKeyboardButton("🎰 Slot", callback_data="slot"),
        InlineKeyboardButton("🎲 Dice", callback_data="dice"),
        InlineKeyboardButton("🎯 Dart", callback_data="dart"),
        InlineKeyboardButton("🎳 Bowling", callback_data="bowling"),
        InlineKeyboardButton("🏀 Basketball", callback_data="basketball")
    ]

    keyboard.add(*buttons)

    bot.send_message(
        message.chat.id,
        "🎮 GAME MENU\n\nဂိမ်းတစ်ခုရွေးပါ 👇",
        reply_markup=keyboard
    )


# ================= GAME BUTTON =================
@bot.callback_query_handler(
    func=lambda call: call.data in [
        "football",
        "slot",
        "dice",
        "dart",
        "bowling",
        "basketball"
    ]
)
def game_buttons(call):

    games = {
        "football": "⚽",
        "slot": "🎰",
        "dice": "🎲",
        "dart": "🎯",
        "bowling": "🎳",
        "basketball": "🏀"
    }

    bot.answer_callback_query(call.id)

    bot.send_dice(
        call.message.chat.id,
        emoji=games[call.data]
    )


# ================= INDIVIDUAL COMMANDS =================
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


# ================= WEB SERVER =================
def run():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )


Thread(target=run).start()

print("Bot is starting...")

bot.infinity_polling()
