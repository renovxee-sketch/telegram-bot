import os
import json
import time
import threading

import telebot
from telebot import types
from flask import Flask


# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(BOT_TOKEN)

OWNER_USERNAME = "Ruifineshyt"
DATA_FILE = "bot_data.json"


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!"


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# =========================================================
# DATA
# =========================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


data = load_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(user_id, first_name="User", username=None):
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "name": first_name,
            "username": username or "",
            "usd": 0,
            "dia": 0
        }
        save_data()
    else:
        data[user_id]["name"] = first_name

        if username:
            data[user_id]["username"] = username

    return data[user_id]


# =========================================================
# HELPERS
# =========================================================

def mention_user(user):
    name = user.first_name or "User"
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def is_owner(message):
    username = message.from_user.username

    if not username:
        return False

    return username.lower() == OWNER_USERNAME.lower()


def money(value):
    return f"{value:,}"


# =========================================================
# BALANCE
# =========================================================

def balance_text(user, user_id):
    return (
        f"👤 {user['name']} ({user_id}) ၏ လက်ကျန်ငွေ\n\n"
        f"💎 Diamonds: {money(user['dia'])}💎\n"
        f"💵 USD: ${money(user['usd'])}USD"
    )


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start_command(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )

    text = (
        f"👋 မင်္ဂလာပါ {mention_user(message.from_user)}!\n\n"
        "🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!\n\n"
        f"💎 Diamonds: {money(user['dia'])}💎\n"
        f"💵 USD: ${money(user['usd'])}USD\n\n"
        "👇 အောက်ပါ Button ကို နှိပ်ပြီး သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "➕ Add Me Your Group",
            url="https://t.me/Ruifineshyt_bot?startgroup=true"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# BALANCE
# =========================================================

@bot.message_handler(commands=["balance"])
def balance_command(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )

    bot.reply_to(
        message,
        balance_text(user, message.from_user.id)
    )


# =========================================================
# GAME
# =========================================================

@bot.message_handler(commands=["game"])
def game_command(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )

    text = (
        "╔════════════════════════╗\n"
        "🎮 GAME CENTER 🎮\n"
        "╚════════════════════════╝\n\n"

        f"👤 {mention_user(message.from_user)}\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "🎰 ဂိမ်းကမ္ဘာမှ ကြိုဆိုပါတယ်!\n\n"

        "ဒီနေရာမှာ သင့်ကံကို စမ်းသပ်ပြီး 🎯\n"
        "စိတ်လှုပ်ရှားဖွယ် Game များကို\n"
        "အပျော်တမ်း ကစားနိုင်ပါတယ်! 🔥\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "💰 သင့်လက်ရှိ Balance\n\n"

        f"💵 USD ┃ ${money(user['usd'])}\n"
        f"💎 DIA ┃ {money(user['dia'])}\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "🎮 လက်ရှိ ကစားနိုင်သော Game\n\n"

        "🎰 SLOT MACHINE\n"
        "└ 🍒 🍋 🍇 7️⃣ BAR\n"
        "└ သင့်ကံကို စမ်းသပ်လိုက်ပါ! 🍀\n\n"

        "👇 အောက်က Game ကိုရွေးပြီး စတင်ကစားပါ!"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🎰 SLOT MACHINE 🎰",
            callback_data="game_slot"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# BET BUTTONS
# =========================================================

BET_AMOUNTS = [
    10,
    100,
    1000,
    10000,
    100000,
    300000,
    500000,
    1000000
]


def bet_name(amount):

    names = {
        10: "10 USD",
        100: "100 USD",
        1000: "1K USD",
        10000: "10K USD",
        100000: "100K USD",
        300000: "300K USD",
        500000: "500K USD",
        1000000: "1M USD"
    }

    return names.get(amount, f"{money(amount)} USD")


def create_bet_keyboard():

    markup = types.InlineKeyboardMarkup()

    row = []

    for amount in BET_AMOUNTS:

        row.append(
            types.InlineKeyboardButton(
                f"💵 {bet_name(amount)}",
                callback_data=f"slot_bet:{amount}"
            )
        )

        if len(row) == 2:
            markup.row(*row)
            row = []

    return markup


# =========================================================
# SLOT OPEN
# =========================================================

@bot.callback_query_handler(func=lambda call: call.data == "game_slot")
def slot_button(call):

    user = get_user(
        call.from_user.id,
        call.from_user.first_name,
        call.from_user.username
    )

    bot.answer_callback_query(call.id)

    text = (
        "🎰 SLOT MACHINE 🎰\n\n"
        f"👤 {mention_user(call.from_user)}\n\n"
        "💰 သင့်လက်ရှိ Balance\n"
        f"💵 USD ┃ ${money(user['usd'])}\n"
        f"💎 DIA ┃ {money(user['dia'])}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💵 ထိုးမယ့် လောင်းကြေးကို ရွေးပါ 👇"
    )

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=create_bet_keyboard(),
        parse_mode="HTML"
    )


# =========================================================
# TELEGRAM SLOT RESULT
# =========================================================

def get_slot_combination(dice_value):

    symbols = [
        "BAR",
        "🍇",
        "🍋",
        "7️⃣"
    ]

    value = dice_value - 1

    left = value & 3
    middle = (value >> 2) & 3
    right = (value >> 4) & 3

    return (
        symbols[left],
        symbols[middle],
        symbols[right]
    )


# =========================================================
# PAYOUT
# =========================================================

def get_slot_payout(dice_value):

    left, middle, right = get_slot_combination(dice_value)

    # 777 = 30x
    if (
        left == "7️⃣"
        and middle == "7️⃣"
        and right == "7️⃣"
    ):
        return 30

    # BAR BAR BAR = 10x
    if (
        left == "BAR"
        and middle == "BAR"
        and right == "BAR"
    ):
        return 10

    # 77🍇 = 3x
    if (
        left == "7️⃣"
        and middle == "7️⃣"
        and right == "🍇"
    ):
        return 3

    # 🍇77 = 3x
    if (
        left == "🍇"
        and middle == "7️⃣"
        and right == "7️⃣"
    ):
        return 3

    # 7🍇7 = NO WIN
    if (
        left == "7️⃣"
        and middle == "🍇"
        and right == "7️⃣"
    ):
        return 0

    # Fruit must be THREE identical fruits
    if left == middle == right:

        if left in ["🍇", "🍋", "🍒"]:
            return 5

    # Two fruits only = NO WIN
    return 0


# =========================================================
# SLOT RESULT MESSAGE
# =========================================================

def send_slot_result(
    chat_id,
    user,
    bet,
    multiplier,
    dice_value
):

    left, middle, right = get_slot_combination(dice_value)

    combination = f"{left}  {middle}  {right}"

    if multiplier > 0:

        winnings = bet * multiplier

        result_text = (
            "🎰 SLOT RESULT 🎰\n\n"

            f"👤 {user['name']}\n\n"

            f"🎰 {combination}\n\n"

            "🎉 ဒီတစ်ခါ နိုင်ပါတယ်!\n"
            f"🏆 ဆုကြေး — {multiplier}×\n"
            f"💰 အနိုင်ရငွေ — ${money(winnings)} USD\n\n"

            "🍀 နောက်တစ်ကြိမ်လည်း ကံကောင်းပါစေ!\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "💰 လက်ရှိ Balance\n"
            f"💵 USD ┃ ${money(user['usd'])}\n"
            f"💎 DIA ┃ {money(user['dia'])}\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "💵 နောက်တစ်ကြိမ် ထိုးမယ့် လောင်းကြေးရွေးပါ 👇"
        )

    else:

        result_text = (
            "🎰 SLOT RESULT 🎰\n\n"

            f"👤 {user['name']}\n\n"

            f"🎰 {combination}\n\n"

            "😢 ဒီတစ်ခါ ရှုံးသွားပါတယ်။\n"
            f"💸 ရှုံးကြေး — ${money(bet)} USD\n\n"

            "🍀 နောက်တစ်ကြိမ် ကံကောင်းပါစေ!\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "💰 လက်ရှိ Balance\n"
            f"💵 USD ┃ ${money(user['usd'])}\n"
            f"💎 DIA ┃ {money(user['dia'])}\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "💵 နောက်တစ်ကြိမ် ထိုးမယ့် လောင်းကြေးရွေးပါ 👇"
        )

    bot.send_message(
        chat_id,
        result_text,
        reply_markup=create_bet_keyboard()
    )


# =========================================================
# SLOT BET
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("slot_bet:")
)
def slot_bet(call):

    try:
        bet = int(
            call.data.split(":")[1]
        )
    except Exception:

        bot.answer_callback_query(
            call.id,
            "❌ လောင်းကြေးမမှန်ပါ။"
        )

        return

    user = get_user(
        call.from_user.id,
        call.from_user.first_name,
        call.from_user.username
    )

    # Balance check
    if user["usd"] < bet:

        bot.answer_callback_query(
            call.id,
            "❌ Balance မလုံလောက်ပါ!",
            show_alert=True
        )

        return

    # Deduct bet
    user["usd"] -= bet
    save_data()

    bot.answer_callback_query(call.id)

    # =====================================================
    # REAL TELEGRAM SLOT ANIMATION
    # =====================================================

    dice_msg = bot.send_dice(
        call.message.chat.id,
        emoji="🎰"
    )

    # Animation အရမ်းမနှေးအောင်
    time.sleep(1.2)

    dice_value = dice_msg.dice.value

    # Payout
    multiplier = get_slot_payout(
        dice_value
    )

    # Add winnings
    if multiplier > 0:

        winnings = bet * multiplier

        user["usd"] += winnings

        save_data()

    # Refresh user
    user = get_user(
        call.from_user.id,
        call.from_user.first_name,
        call.from_user.username
    )

    # Result
    send_slot_result(
        call.message.chat.id,
        user,
        bet,
        multiplier,
        dice_value
    )


# =========================================================
# OWNER USD
# =========================================================

@bot.message_handler(commands=["usd"])
def usd_command(message):

    if not is_owner(message):

        bot.reply_to(
            message,
            "❌ Owner only."
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "အသုံးပြုပုံ\n\n/usd 100"
        )

        return

    try:
        amount = int(parts[1])
    except ValueError:

        bot.reply_to(
            message,
            "❌ Amount မမှန်ပါ။"
        )

        return

    user = get_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )

    user["usd"] += amount

    save_data()

    bot.reply_to(
        message,
        f"✅ USD ${money(amount)} ထည့်ပြီးပါပြီ။\n\n"
        f"💵 Balance ┃ ${money(user['usd'])}"
    )


# =========================================================
# OWNER DIA
# =========================================================

@bot.message_handler(commands=["dia"])
def dia_command(message):

    if not is_owner(message):

        bot.reply_to(
            message,
            "❌ Owner only."
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "အသုံးပြုပုံ\n\n/dia 100"
        )

        return

    try:
        amount = int(parts[1])
    except ValueError:

        bot.reply_to(
            message,
            "❌ Amount မမှန်ပါ။"
        )

        return

    user = get_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )

    user["dia"] += amount

    save_data()

    bot.reply_to(
        message,
        f"✅ Diamonds {money(amount)}💎 ထည့်ပြီးပါပြီ။\n\n"
        f"💎 Balance ┃ {money(user['dia'])}💎"
    )


# =========================================================
# GIFT USD
# =========================================================

@bot.message_handler(commands=["gift"])
def gift_command(message):

    if not is_owner(message):

        bot.reply_to(
            message,
            "❌ Owner only."
        )

        return

    if not message.reply_to_message:

        bot.reply_to(
            message,
            "❌ User ရဲ့ message ကို Reply လုပ်ပြီး\n"
            "/gift amount\n\n"
            "ဥပမာ - /gift 100"
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "❌ Amount ထည့်ပါ။\n\n"
            "ဥပမာ - /gift 100"
        )

        return

    try:
        amount = int(parts[1])
    except ValueError:

        bot.reply_to(
            message,
            "❌ Amount မမှန်ပါ။"
        )

        return

    target = message.reply_to_message.from_user

    user = get_user(
        target.id,
        target.first_name,
        target.username
    )

    user["usd"] += amount

    save_data()

    bot.reply_to(
        message,
        f"🎁 USD Gift ပေးပြီးပါပြီ!\n\n"
        f"👤 {target.first_name}\n"
        f"💵 +${money(amount)} USD\n"
        f"💰 Balance ┃ ${money(user['usd'])}"
    )


# =========================================================
# GIFT DIA
# =========================================================

@bot.message_handler(commands=["giftdia"])
def giftdia_command(message):

    if not is_owner(message):

        bot.reply_to(
            message,
            "❌ Owner only."
        )

        return

    if not message.reply_to_message:

        bot.reply_to(
            message,
            "❌ User ရဲ့ message ကို Reply လုပ်ပြီး\n"
            "/giftdia amount\n\n"
            "ဥပမာ - /giftdia 100"
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "❌ Amount ထည့်ပါ။\n\n"
            "ဥပမာ - /giftdia 100"
        )

        return

    try:
        amount = int(parts[1])
    except ValueError:

        bot.reply_to(
            message,
            "❌ Amount မမှန်ပါ။"
        )

        return

    target = message.reply_to_message.from_user

    user = get_user(
        target.id,
        target.first_name,
        target.username
    )

    user["dia"] += amount

    save_data()

    bot.reply_to(
        message,
        f"🎁 Diamonds Gift ပေးပြီးပါပြီ!\n\n"
        f"👤 {target.first_name}\n"
        f"💎 +{money(amount)} DIA\n"
        f"💎 Balance ┃ {money(user['dia'])}"
    )


# =========================================================
# COMMAND MENU
# =========================================================

def setup_commands():

    commands = [
        types.BotCommand(
            "start",
            "Bot စတင်ရန်"
        ),
        types.BotCommand(
            "game",
            "Game ကစားရန်"
        ),
        types.BotCommand(
            "balance",
            "Balance ကြည့်ရန်"
        ),
        types.BotCommand(
            "gift",
            "USD Gift ပေးရန်"
        ),
        types.BotCommand(
            "giftdia",
            "Diamond Gift ပေးရန်"
        )
    ]

    bot.set_my_commands(commands)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    setup_commands()

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    print("Bot is running...")

    bot.remove_webhook()

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
)
