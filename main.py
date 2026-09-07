import os
import json
import time
import random
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


# =========================
# DATA SYSTEM
# =========================

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {"users": {}}


data = load_data()
users = data.get("users", {})


def save_data():
    data["users"] = users

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


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


# =========================
# COMMAND MENU
# =========================

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
            "Game Center"
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
        )
    ]

    bot.set_my_commands(commands)


# =========================
# /START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(user_id)

    text = (
        f"👋 မင်္ဂလာပါ "
        f'<a href="tg://user?id={user_id}">{user_name}</a>!\n\n'

        "🎮 <b>အပျော်တမ်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!</b>\n\n"

        f"💎 Diamonds: {user['dia']:,}\n"
        f"💵 USD: ${user['usd']:,}\n\n"

        "👇 အောက်ပါ Button ကို နှိပ်ပြီး "
        "သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!"
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


# =========================
# /BALANCE
# =========================

@bot.message_handler(commands=["balance"])
def balance(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(user_id)

    text = (
        "╔══════════════════════╗\n"
        "💰 <b>YOUR BALANCE</b> 💰\n"
        "╚══════════════════════╝\n\n"

        f"👤 <b>{user_name}</b>\n\n"

        f"💎 Diamonds ┃ <b>{user['dia']:,}</b>\n"
        f"💵 USD ┃ <b>{user['usd']:,} USD</b>"
    )

    bot.reply_to(
        message,
        text,
        parse_mode="HTML"
    )


# =========================
# /GAME
# =========================

@bot.message_handler(commands=["game"])
def game(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(user_id)

    text = (
        "╔════════════════════════╗\n"
        "🎮 <b>GAME CENTER</b> 🎮\n"
        "╚════════════════════════╝\n\n"

        f"👤 <a href='tg://user?id={user_id}'><b>{user_name}</b></a>\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "🎰 <b>ဂိမ်းကမ္ဘာမှ ကြိုဆိုပါတယ်!</b>\n\n"

        "ဒီနေရာမှာ သင့်ကံကို စမ်းသပ်ပြီး 🎯\n"
        "စိတ်လှုပ်ရှားဖွယ် Game များကို\n"
        "အပျော်တမ်း ကစားနိုင်ပါတယ်! 🔥\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "💰 <b>သင့်လက်ရှိ Balance</b>\n\n"

        f"💵 USD ┃ <b>{user['usd']:,} USD</b>\n"
        f"💎 DIA ┃ <b>{user['dia']:,} Diamonds</b>\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "🎮 <b>လက်ရှိ ကစားနိုင်သော Game</b>\n\n"

        "🎰 <b>SLOT MACHINE</b>\n"
        "└ 🍒 🍋 🍇 7️⃣ BAR\n"
        "└ သင့်ကံကို စမ်းသပ်လိုက်ပါ! 🍀\n\n"

        "👇 <b>အောက်က Game ကိုရွေးပြီး စတင်ကစားပါ!</b>"
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "🎰  SLOT MACHINE  🎰",
            callback_data="game_slot"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# =========================
# BET BUTTONS
# =========================

def slot_bet_keyboard():

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            "💵 10 USD",
            callback_data="slot_bet_10"
        ),

        InlineKeyboardButton(
            "💵 100 USD",
            callback_data="slot_bet_100"
        ),

        InlineKeyboardButton(
            "💵 1K USD",
            callback_data="slot_bet_1000"
        ),

        InlineKeyboardButton(
            "💵 10K USD",
            callback_data="slot_bet_10000"
        ),

        InlineKeyboardButton(
            "💵 100K USD",
            callback_data="slot_bet_100000"
        ),

        InlineKeyboardButton(
            "💵 300K USD",
            callback_data="slot_bet_300000"
        ),

        InlineKeyboardButton(
            "💵 500K USD",
            callback_data="slot_bet_500000"
        ),

        InlineKeyboardButton(
            "💵 1M USD",
            callback_data="slot_bet_1000000"
        )
    )

    return keyboard


# =========================
# SLOT MACHINE BUTTON
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "game_slot"
)
def slot_button(call):

    bot.answer_callback_query(call.id)

    user = get_user(call.from_user.id)

    text = (
        "╔════════════════════════╗\n"
        "🎰 <b>SLOT MACHINE</b> 🎰\n"
        "╚════════════════════════╝\n\n"

        f"💰 <b>Balance: {user['usd']:,} USD</b>\n\n"

        "🎯 လောင်းကြေးပမာဏကို ရွေးချယ်ပြီး\n"
        "🎰 SLOT MACHINE ကို စတင်လှည့်လိုက်ပါ!\n\n"

        "👇 <b>လောင်းကြေးရွေးပါ</b>"
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=slot_bet_keyboard(),
        parse_mode="HTML"
    )


# =========================
# SLOT GAME
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("slot_bet_")
)
def slot_bet(call):

    try:

        bet = int(
            call.data.replace(
                "slot_bet_",
                ""
            )
        )

    except ValueError:

        bot.answer_callback_query(
            call.id,
            "❌ Bet Error",
            show_alert=True
        )

        return


    # =========================
    # GET USER BALANCE
    # =========================

    user = get_user(
        call.from_user.id
    )

    balance = int(
        user.get("usd", 0)
    )


    # =========================
    # NOT ENOUGH MONEY
    # =========================

    if balance < bet:

        bot.answer_callback_query(
            call.id,
            "❌ လောင်းကြေးမလောက်ပါ!",
            show_alert=True
        )

        text = (
            "╔════════════════════════╗\n"
            "🎰 <b>SLOT MACHINE</b> 🎰\n"
            "╚════════════════════════╝\n\n"

            "❌ <b>လောင်းကြေးမလောက်ပါ!</b>\n\n"

            f"💵 လောင်းမည့်ငွေ ┃ "
            f"<b>{bet:,} USD</b>\n"

            f"💰 သင့် Balance ┃ "
            f"<b>{balance:,} USD</b>\n\n"

            "⚠️ <b>Balance ထက်များတဲ့ Bet ကို\n"
            "လောင်းလို့မရပါဘူး။</b>\n\n"

            "👇 <b>လောင်းကြေးအသစ် ရွေးပါ</b>"
        )

        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=slot_bet_keyboard(),
            parse_mode="HTML"
        )

        return


    # =========================
    # DEDUCT BET
    # =========================

    user["usd"] -= bet

    save_data()


    bot.answer_callback_query(
        call.id,
        f"🎰 {bet:,} USD လောင်းပြီးပါပြီ!"
    )


    chat_id = call.message.chat.id
    message_id = call.message.message_id


    # =========================
    # ANIMATION 1
    # =========================

    bot.edit_message_text(

        "🎰 <b>SLOT MACHINE</b>\n\n"

        "🔄 <b>လှည့်နေပါတယ်...</b>\n\n"

        "🍒 │ 🍋 │ 🍇\n\n"

        f"💵 Bet ┃ <b>{bet:,} USD</b>\n"
        f"💰 Balance ┃ <b>{user['usd']:,} USD</b>",

        chat_id,
        message_id,

        parse_mode="HTML"
    )

    time.sleep(0.7)


    # =========================
    # ANIMATION 2
    # =========================

    bot.edit_message_text(

        "🎰 <b>SLOT MACHINE</b>\n\n"

        "🔄 <b>လှည့်နေပါတယ်...</b>\n\n"

        "🍋 │ 🍇 │ 7️⃣\n\n"

        f"💵 Bet ┃ <b>{bet:,} USD</b>\n"
        f"💰 Balance ┃ <b>{user['usd']:,} USD</b>",

        chat_id,
        message_id,

        parse_mode="HTML"
    )

    time.sleep(0.7)


    # =========================
    # ANIMATION 3
    # =========================

    bot.edit_message_text(

        "🎰 <b>SLOT MACHINE</b>\n\n"

        "🔄 <b>လှည့်နေပါတယ်...</b>\n\n"

        "🍇 │ 7️⃣ │ 🍒\n\n"

        f"💵 Bet ┃ <b>{bet:,} USD</b>\n"
        f"💰 Balance ┃ <b>{user['usd']:,} USD</b>",

        chat_id,
        message_id,

        parse_mode="HTML"
    )

    time.sleep(0.7)


    # =========================
    # RANDOM RESULT
    # =========================

    symbols = [
        "🍒",
        "🍋",
        "🍇",
        "🍊",
        "7️⃣",
        "BAR"
    ]

    result = [
        random.choice(symbols),
        random.choice(symbols),
        random.choice(symbols)
    ]

    result_text = " │ ".join(result)


    # =========================
    # RESULT
    # =========================

    bot.edit_message_text(

        "╔════════════════════════╗\n"
        "🎰 <b>SLOT RESULT</b> 🎰\n"
        "╚════════════════════════╝\n\n"

        f"🎲 <b>{result_text}</b>\n\n"

        f"💵 လောင်းကြေး ┃ "
        f"<b>{bet:,} USD</b>\n"

        f"💰 လက်ကျန် ┃ "
        f"<b>{user['usd']:,} USD</b>\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "🎰 <b>နောက်တစ်ပွဲ ကစားမလား?</b>\n\n"

        "👇 <b>လောင်းကြေးအသစ် ရွေးပါ</b>",

        chat_id,
        message_id,

        reply_markup=slot_bet_keyboard(),

        parse_mode="HTML"
    )


# =========================
# /USD
# =========================

@bot.message_handler(commands=["usd"])
def add_usd(message):

    if not is_owner(message):

        bot.reply_to(
            message,
            "❌ ဒီ Command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။"
        )

        return


    parts = message.text.split()

    if len(parts) != 2:

        bot.reply_to(
            message,
            "❌ ဥပမာ - /usd 50000"
        )

        return


    try:

        amount = int(parts[1])

    except ValueError:

        bot.reply_to(
            message,
            "❌ USD ပမာဏကို နံပါတ်နဲ့ ထည့်ပါ။"
        )

        return


    if amount <= 0:

        bot.reply_to(
            message,
            "❌ 0 ထက်ကြီးတဲ့ ပမာဏထည့်ပါ။"
        )

        return


    user = get_user(
        message.from_user.id
    )

    user["usd"] += amount

    save_data()


    bot.reply_to(

        message,

        f"✅ USD ထည့်ပြီးပါပြီ!\n\n"
        f"💵 +${amount:,}\n"
        f"💰 လက်ကျန်: "
        f"${user['usd']:,} USD"
    )


# =========================
# /DIA
# =========================

@bot.message_handler(commands=["dia"])
def add_diamond(message):

    if not is_owner(message):

        bot.reply_to(
            message,
            "❌ ဒီ Command ကို Owner သာ အသုံးပြုနိုင်ပါတယ်။"
        )

        return


    parts = message.text.split()

    if len(parts) != 2:

        bot.reply_to(
            message,
            "❌ ဥပမာ - /dia 100000"
        )

        return


    try:

        amount = int(parts[1])

    except ValueError:

        bot.reply_to(
            message,
            "❌ Diamond ပမာဏကို နံပါတ်နဲ့ ထည့်ပါ။"
        )

        return


    if amount <= 0:

        bot.reply_to(
            message,
            "❌ 0 ထက်ကြီးတဲ့ ပမာဏထည့်ပါ။"
        )

        return


    user = get_user(
        message.from_user.id
    )

    user["dia"] += amount

    save_data()


    bot.reply_to(

        message,

        f"✅ Diamond ထည့်ပြီးပါပြီ!\n\n"
        f"💎 +{amount:,}\n"
        f"💎 လက်ကျန်: "
        f"{user['dia']:,} Diamonds"
    )


# =========================
# /GIFTUSD
# =========================

@bot.message_handler(commands=["giftusd"])
def gift_usd(message):

    if not is_owner(message):

        bot.reply_to(
            message,
            "❌ Owner သာ အသုံးပြုနိုင်ပါတယ်။"
        )

        return


    if not message.reply_to_message:

        bot.reply_to(
            message,
            "❌ ပေးမယ့်သူရဲ့ Message ကို Reply လုပ်ပါ။"
        )

        return


    parts = message.text.split()

    if len(parts) != 2:

        bot.reply_to(
            message,
            "❌ ဥပမာ - /giftusd 50"
        )

        return


    try:

        amount = int(parts[1])

    except ValueError:

        bot.reply_to(
            message,
            "❌ USD ပမာဏကို နံပါတ်နဲ့ ထည့်ပါ။"
        )

        return


    if amount <= 0:

        bot.reply_to(
            message,
            "❌ 0 ထက်ကြီးတဲ့ ပမာဏထည့်ပါ။"
        )

        return


    target = message.reply_to_message.from_user


    keyboard = InlineKeyboardMarkup()

    keyboard.row(

        InlineKeyboardButton(
            "✅ Confirm",
            callback_data=(
                f"confirm_usd_"
                f"{target.id}_"
                f"{amount}"
            )
        ),

        InlineKeyboardButton(
            "❌ Cancel",
            callback_data="cancel_usd"
        )
    )


    target_name = (
        target.first_name or "Player"
    )


    text = (

        "🎁 <b>USD Gift အတည်ပြုရန်</b>\n\n"

        f"👤 {target_name}\n"

        f"💵 ပေးမည့်ပမာဏ: "
        f"<b>${amount:,} USD</b>\n\n"

        "အတည်ပြုမယ်ဆိုရင် "
        "✅ Confirm ကိုနှိပ်ပါ။"
    )


    bot.reply_to(

        message,
        text,

        reply_markup=keyboard,

        parse_mode="HTML"
    )


# =========================
# CONFIRM USD
# =========================

@bot.callback_query_handler(
    func=lambda call:
        call.data.startswith("confirm_usd_")
)
def confirm_usd(call):

    username = call.from_user.username

    if (
        not username
        or username.lower()
        != OWNER_USERNAME.lower()
    ):

        bot.answer_callback_query(
            call.id,
            "❌ Owner သာ Confirm လုပ်နိုင်ပါတယ်။",
            show_alert=True
        )

        return


    try:

        parts = call.data.split("_")

        target_id = int(parts[2])
        amount = int(parts[3])

    except Exception:

        bot.answer_callback_query(
            call.id,
            "❌ Error ဖြစ်သွားပါတယ်။",
            show_alert=True
        )

        return


    user = get_user(target_id)

    user["usd"] += amount

    save_data()


    bot.answer_callback_query(
        call.id,
        "✅ USD Gift ပေးပြီးပါပြီ!"
    )


    bot.edit_message_text(

        "🎁 <b>USD Gift ပေးပြီးပါပြီ!</b>\n\n"
        f"💵 +${amount:,} USD",

        call.message.chat.id,
        call.message.message_id,

        parse_mode="HTML"
    )


# =========================
# CANCEL USD
# =========================

@bot.callback_query_handler(
    func=lambda call:
        call.data == "cancel_usd"
)
def cancel_usd(call):

    username = call.from_user.username

    if (
        not username
        or username.lower()
        != OWNER_USERNAME.lower()
    ):

        bot.answer_callback_query(
            call.id,
            "❌ Owner သာ Cancel လုပ်နိုင်ပါတယ်။",
            show_alert=True
        )

        return


    bot.answer_callback_query(
        call.id,
        "❌ Gift Cancel လုပ်ပြီးပါပြီ။"
    )


    bot.edit_message_text(

        "❌ <b>USD Gift Cancel လုပ်ပြီးပါပြီ။</b>",

        call.message.chat.id,
        call.message.message_id,

        parse_mode="HTML"
    )


# =========================
# FLASK
# =========================

@app.route("/")
def home():

    return "Game Bot is running!"


def run():

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )


Thread(
    target=run,
    daemon=True
).start()


# =========================
# START BOT
# =========================

print("Bot is starting...")


try:

    bot.remove_webhook()

except Exception:

    pass


set_commands()


bot.infinity_polling(
    skip_pending=True,
    timeout=20,
    long_polling_timeout=20
)
