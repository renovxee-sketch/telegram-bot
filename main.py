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
        "🎮 ဆော့ကစားနိုင်သောဂိမ်းများ\n\nဂိမ်းတစ်ခုရွေးပါ 👇",
        reply_markup=keyboard
    )


# ================= GAME SELECT =================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("game_")
)
def select_game(call):

    bot.answer_callback_query(call.id)

    game_name = call.data.replace("game_", "")

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("💰 10", callback_data=f"money_{game_name}_10"),
        InlineKeyboardButton("💰 100", callback_data=f"money_{game_name}_100"),

        InlineKeyboardButton("💰 1K", callback_data=f"money_{game_name}_1000"),
        InlineKeyboardButton("💰 10K", callback_data=f"money_{game_name}_10000"),

        InlineKeyboardButton("💰 100K", callback_data=f"money_{game_name}_100000"),
        InlineKeyboardButton("💰 300K", callback_data=f"money_{game_name}_300000"),

        InlineKeyboardButton("💰 500K", callback_data=f"money_{game_name}_500000"),
        InlineKeyboardButton("💰 1M", callback_data=f"money_{game_name}_1000000")
    )

    bot.edit_message_text(
        f"🎮 {game_name.upper()}\n\n💰 လောင်းကြေးပမာဏရွေးပါ 👇",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )


# ================= MONEY SELECT =================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("money_")
)
def select_money(call):

    bot.answer_callback_query(call.id)

    parts = call.data.split("_")

    game = parts[1]
    money = parts[2]

    bot.edit_message_text(
        f"🎮 Game: {game.upper()}\n\n"
        f"💰 လောင်းကြေး: {money}\n\n"
        f"🎯 ဂိမ်းစတင်ရန် အဆင့် ၃ မှာ ဆက်လုပ်မယ် 👇",
        call.message.chat.id,
        call.message.message_id
    )


# ================= INDIVIDUAL GAME COMMANDS =================

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
