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

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=keyboard
    )

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

def run():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

Thread(target=run).start()
bot.infinity_polling()
