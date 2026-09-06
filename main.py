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


@bot.message_handler(commands=["start"])
def start(message):
    text = """
👋 မင်္ဂလာပါ Takemichi Hanagaki!

🎮 အပျော်တန်းGameကစားတဲ့Bot မှ ကြိုဆိုပါတယ်!

👇 အောက်ပါ Button ကို နှိပ်ပြီး
သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!
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
    bot.send_dice(message.chat
