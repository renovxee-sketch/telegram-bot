import os
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
    return "Game Bot is running!"


# =========================
# START COMMAND
# =========================
@bot.message_handler(commands=["start"])
def start(message):

    user_name = message.from_user.first_name or "Player"
    user_id = message.from_user.id

    text = (
        f'👋 မင်္ဂလာပါ <a href="tg://user?id={user_id}">'
        f'{user_name}</a>!\n\n'
        f'🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!\n\n'
        f'👇 အောက်ပါ Button ကို နှိပ်ပြီး သင့် Group ထဲသို့ '
        f'Bot ကို ထည့်သွင်းနိုင်ပါတယ်!'
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


# =========================
# GAME MENU
# =========================
@bot.message_handler(commands=["game"])
def game_menu(message):

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("⚽ Football", callback_data="football"),
        InlineKeyboardButton("🎰 Slot", callback_data="slot")
    )

    keyboard.add(
        InlineKeyboardButton("🎲 Dice", callback_data="dice"),
        InlineKeyboardButton("🎯 Dart", callback_data="dart")
    )

    keyboard.add(
        InlineKeyboardButton("🎳 Bowling", callback_data="bowling"),
        InlineKeyboardButton("🏀 Basketball", callback_data="basketball")
    )

    bot.send_message(
        message.chat.id,
        "🎮 GAME MENU\n\nဂိမ်းတစ်ခုရွေးပါ 👇",
        reply_markup=keyboard
    )


# =========================
# GAME BUTTONS
# =========================
@bot.callback_query_handler(func=lambda call: True)
def game_buttons(call):

    if call.data == "football":
        bot.send_dice(call.message.chat.id, emoji="⚽")

    elif call.data == "slot":
        bot.send_dice(call.message.chat.id, emoji="🎰")

    elif call.data == "dice":
        bot.send_dice(call.message.chat.id, emoji="🎲")

    elif call.data == "dart":
        bot.send_dice(call.message.chat.id, emoji="🎯")

    elif call.data == "bowling":
        bot.send_dice(call.message.chat.id, emoji="🎳")

    elif call.data == "basketball":
        bot.send_dice(call.message.chat.id, emoji="🏀")

    bot.answer_callback_query(call.id)


# =========================
# INDIVIDUAL GAME COMMANDS
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


Thread(target=run).start()

bot.infinity_polling()
