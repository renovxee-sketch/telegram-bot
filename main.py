import os
import json
import time
import telebot

from flask import Flask
from threading import Thread
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(BOT_TOKEN)

OWNER_USERNAME = "Ruifineshyt"

DATA_FILE = "bot_data.json"


# ============================================================
# DATA
# ============================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


data = load_data()


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )
    except Exception as e:
        print("Save error:", e)


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

    if "usd" not in data[user_id]:
        data[user_id]["usd"] = 0

    if "dia" not in data[user_id]:
        data[user_id]["dia"] = 0

    return data[user_id]


# ============================================================
# OWNER
# ============================================================

def is_owner(message):

    username = message.from_user.username

    if not username:
        return False

    return username.lower() == OWNER_USERNAME.lower()


# ============================================================
# BOT COMMAND MENU
# ============================================================

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


# ============================================================
# USER MENTION
# ============================================================

def user_mention(user):

    name = user.first_name or "User"
    user_id = user.id

    return (
        f'<a href="tg://user?id={user_id}">'
        f'{name}'
        f'</a>'
    )


# ============================================================
# START
# ============================================================

@bot.message_handler(commands=["start"])
def start(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name
    )

    mention = user_mention(message.from_user)

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


# ============================================================
# BALANCE
# ============================================================

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

    bot.reply_to(
        message,
        text
    )


# ============================================================
# GAME CENTER
# ============================================================

@bot.message_handler(commands=["game"])
def game(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name
    )

    mention = user_mention(message.from_user)

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


# ============================================================
# SLOT BET KEYBOARD
# ============================================================

def slot_bet_keyboard():

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "💵 10 USD",
            callback_data="slot_bet_10"
        ),
        InlineKeyboardButton(
            "💵 100 USD",
            callback_data="slot_bet_100"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            "💵 1K USD",
            callback_data="slot_bet_1000"
        ),
        InlineKeyboardButton(
            "💵 10K USD",
            callback_data="slot_bet_10000"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            "💵 100K USD",
            callback_data="slot_bet_100000"
        ),
        InlineKeyboardButton(
            "💵 300K USD",
            callback_data="slot_bet_300000"
        )
    )

    keyboard.row(
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


# ============================================================
# OPEN SLOT
# ============================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "game_slot"
)
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


# ============================================================
# SLOT BET
# ============================================================

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
    except Exception:
        bot.answer_callback_query(
            call.id,
            "❌ Bet မမှန်ပါ!",
            show_alert=True
        )
        return

    user = get_user(
        call.from_user.id,
        call.from_user.first_name
    )

    balance = int(
        user.get("usd", 0)
    )

    # --------------------------------------------------------
    # BALANCE CHECK
    # --------------------------------------------------------

    if balance < bet:

        bot.answer_callback_query(
            call.id,
            "❌ လောင်းကြေး မလောက်ပါ!",
            show_alert=True
        )

        return

    # --------------------------------------------------------
    # DEDUCT BET
    # --------------------------------------------------------

    user["usd"] = balance - bet

    save_data()

    bot.answer_callback_query(
        call.id,
        "🎰 Game စတင်ပါပြီ!"
    )

    # --------------------------------------------------------
    # TELEGRAM REAL SLOT ANIMATION
    # --------------------------------------------------------

    dice_message = bot.send_dice(
        call.message.chat.id,
        emoji="🎰"
    )

    # Telegram client မှာ animation ပြရန်
    time.sleep(4)

    # --------------------------------------------------------
    # TELEGRAM SLOT VALUE
    # --------------------------------------------------------

    dice_value = dice_message.dice.value

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if dice_value in [1, 22, 43, 64]:

        result = """
🎉 JACKPOT! 🎉

🔥 အရမ်းကံကောင်းပါတယ်!
🍀 နိုင်ပါတယ်!
"""

    elif dice_value in [16, 32, 48, 63]:

        result = """
🎉 နိုင်ပါတယ်! 🎉

🍀 ကံကောင်းပါတယ်!
"""

    else:

        result = """
😢 ဒီတစ်ခါ ရှုံးသွားပါတယ်။

🍀 နောက်တစ်ကြိမ် ကံကောင်းပါစေ!
"""

    # --------------------------------------------------------
    # NEW RESULT MESSAGE
    # --------------------------------------------------------

    result_text = f"""
🎰 SLOT RESULT 🎰

👤 {call.from_user.first_name}

{result}

━━━━━━━━━━━━━━━━━━━━

💰 လက်ရှိ Balance

💵 USD ┃ ${user["usd"]:,}
💎 DIA ┃ {user["dia"]:,}
"""

    bot.send_message(
        call.message.chat.id,
        result_text
    )


# ============================================================
# OWNER USD
# ============================================================

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

    except Exception:

        bot.reply_to(
            message,
            "❌ Amount မှားနေပါတယ်!"
        )

        return

    if amount <= 0:

        bot.reply_to(
            message,
            "❌ Amount မှားနေပါတယ်!"
        )

        return

    user = get_user(
        message.from_user.id,
        message.from_user.first_name
    )

    user["usd"] += amount

    save_data()

    bot.reply_to(
        message,
        f"""
✅ ${amount:,} USD ထည့်ပြီးပါပြီ!

💵 Balance: ${user["usd"]:,} USD
"""
    )


# ============================================================
# OWNER DIAMONDS
# ============================================================

@bot.message_handler(commands=["dia"])
def add_dia(message):

    if not is_owner(message):
        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "အသုံးပြုပုံ:\n/dia 1000"
        )

        return

    try:
        amount = int(parts[1])

    except Exception:

        bot.reply_to(
            message,
            "❌ Amount မှားနေပါတယ်!"
        )

        return

    if amount <= 0:

        bot.reply_to(
            message,
            "❌ Amount မှားနေပါတယ်!"
        )

        return

    user = get_user(
        message.from_user.id,
        message.from_user.first_name
    )

    user["dia"] += amount

    save_data()

    bot.reply_to(
        message,
        f"""
✅ {amount:,}💎 ထည့်ပြီးပါပြီ!

💎 Diamonds: {user["dia"]:,}💎
"""
    )


# ============================================================
# GIFT USD
# ============================================================

@bot.message_handler(commands=["giftusd"])
def gift_usd(message):

    if not is_owner(message):
        return

    if not message.reply_to_message:

        bot.reply_to(
            message,
            """
❌ User ရဲ့ Message ကို Reply လုပ်ပြီး

/giftusd 1000

လို့ ရိုက်ပါ။
"""
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "အသုံးပြုပုံ:\n/giftusd 1000"
        )

        return

    try:
        amount = int(parts[1])

    except Exception:

        bot.reply_to(
            message,
            "❌ Amount မှားနေပါတယ်!"
        )

        return

    if amount <= 0:
        return

    target = message.reply_to_message.from_user

    target_user = get_user(
        target.id,
        target.first_name
    )

    target_user["usd"] += amount

    save_data()

    bot.reply_to(
        message,
        f"""
🎁 {target.first_name} ကို
${amount:,} USD ပေးပြီးပါပြီ!

💵 Balance: ${target_user["usd"]:,} USD
"""
    )


# ============================================================
# FLASK FOR RENDER
# ============================================================

app = Flask(__name__)


@app.route("/")
def home():

    return "Bot is running!"


def run_server():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )


# ============================================================
# RUN BOT
# ============================================================

if __name__ == "__main__":

    Thread(
        target=run_server,
        daemon=True
    ).start()

    # Telegram webhook ရှိရင် ဖယ်
    try:
        bot.remove_webhook()
    except Exception as e:
        print("Webhook:", e)

    # Command menu
    try:
        set_commands()
    except Exception as e:
        print("Commands:", e)

    print("🤖 Bot is starting...")

    bot.infinity_polling(
        skip_pending=True,
        timeout=60,
        long_polling_timeout=60
    )
