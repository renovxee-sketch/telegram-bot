import os
import random
import time
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN မတွေ့ပါ။ Render Environment Variables မှာ BOT_TOKEN ထည့်ပါ။")

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

users = {}


@app.route("/")
def home():
    return "Game Bot is running!"


# ================= START =================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    if user_id not in users:
        users[user_id] = {
            "usd": 10000
        }

    usd_balance = users[user_id]["usd"]

    text = (
        f'👋 မင်္ဂလာပါ <a href="tg://user?id={user_id}">{user_name}</a>!\n\n'
        f'🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!\n\n'
        f'💵 USD Balance: ${usd_balance:,}\n\n'
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

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "⚽ Football Game",
            callback_data="game_football"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "🎰 Slot Game",
            callback_data="game_slot"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "🎲 Dice Game",
            callback_data="game_dice"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "🎯 Dart Game",
            callback_data="game_dart"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "🎳 Bowling Game",
            callback_data="game_bowling"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "🏀 Basketball Game",
            callback_data="game_basketball"
        )
    )

    bot.send_message(
        message.chat.id,
        "🎮 ဆော့ကစားနိုင်သောဂိမ်းများ\n\n"
        "👇 သင်ကစားလိုသော Game ကို ရွေးချယ်ပါ။",
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
        InlineKeyboardButton("💵 10 USD", callback_data=f"money_{game_name}_10"),
        InlineKeyboardButton("💵 100 USD", callback_data=f"money_{game_name}_100")
    )

    keyboard.add(
        InlineKeyboardButton("💵 1K USD", callback_data=f"money_{game_name}_1000"),
        InlineKeyboardButton("💵 10K USD", callback_data=f"money_{game_name}_10000")
    )

    keyboard.add(
        InlineKeyboardButton("💵 100K USD", callback_data=f"money_{game_name}_100000"),
        InlineKeyboardButton("💵 300K USD", callback_data=f"money_{game_name}_300000")
    )

    keyboard.add(
        InlineKeyboardButton("💵 500K USD", callback_data=f"money_{game_name}_500000"),
        InlineKeyboardButton("💵 1M USD", callback_data=f"money_{game_name}_1000000")
    )

    bot.edit_message_text(
        f"🎮 {game_name.upper()} GAME\n\n"
        "💰 သင်ထိုးလိုသော ငွေပမာဏကို ရွေးချယ်ပါ 👇",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )


# ================= MONEY SELECT =================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("money_")
)
def play_game(call):

    bot.answer_callback_query(call.id)

    user_id = call.from_user.id

    if user_id not in users:
        users[user_id] = {
            "usd": 10000
        }

    parts = call.data.split("_")

    game = parts[1]
    money = int(parts[2])

    usd_balance = users[user_id]["usd"]

    if usd_balance < money:

        bot.edit_message_text(
            "❌ USD Balance မလုံလောက်ပါ!\n\n"
            f"💵 သင့်လက်ကျန်ငွေ: ${usd_balance:,}\n"
            f"💰 လိုအပ်သောငွေ: ${money:,}",
            call.message.chat.id,
            call.message.message_id
        )

        return

    game_emoji = {
        "football": "⚽",
        "slot": "🎰",
        "dice": "🎲",
        "dart": "🎯",
        "bowling": "🎳",
        "basketball": "🏀"
    }

    emoji = game_emoji.get(game, "🎮")

    # Animation 1
    bot.edit_message_text(
        f"{emoji} Game စတင်နေပါသည်.\n\n⏳",
        call.message.chat.id,
        call.message.message_id
    )

    time.sleep(1)

    # Animation 2
    bot.edit_message_text(
        f"{emoji} Game စတင်နေပါသည်..\n\n"
        f"⏳ ⏳",
        call.message.chat.id,
        call.message.message_id
    )

    time.sleep(1)

    # Animation 3
    bot.edit_message_text(
        f"{emoji} Game စတင်နေပါသည်...\n\n"
        f"{emoji} {emoji} {emoji}",
        call.message.chat.id,
        call.message.message_id
    )

    time.sleep(1)

    # Result
    win = random.choice([True, False])

    result_number = random.randint(1, 6)

    if win:

        profit = money
        users[user_id]["usd"] += profit

        bot.edit_message_text(
            f"{emoji} ရလဒ်: {result_number}\n\n"
            "🎉 နိုင်ပါသည်!\n\n"
            f"💰 အသားတင်: +{profit:,} USD\n\n"
            f"💵 လက်ကျန်ငွေ: ${users[user_id]['usd']:,}",
            call.message.chat.id,
            call.message.message_id
        )

    else:

        users[user_id]["usd"] -= money

        bot.edit_message_text(
            f"{emoji} ရလဒ်: {result_number}\n\n"
            "💔 ရှုံးပါသည်!\n\n"
            f"💰 အသားတင်: -{money:,} USD\n\n"
            f"💵 လက်ကျန်ငွေ: ${users[user_id]['usd']:,}",
            call.message.chat.id,
            call.message.message_id
        )


# ================= GAME COMMANDS =================

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
