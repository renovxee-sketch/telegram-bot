import os
import time
import threading

import telebot
from telebot import types
from flask import Flask
from pymongo import MongoClient


# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set!")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set!")


bot = telebot.TeleBot(BOT_TOKEN)

OWNER_USERNAME = "Ruifineshyt"

WELCOME_USD = 20000
WELCOME_DIA = 500

app = Flask(__name__)


# =========================================================
# MONGODB
# =========================================================

mongo_client = MongoClient(MONGO_URI)

db = mongo_client["casino_bot"]

users_collection = db["users"]


# =========================================================
# FLASK
# =========================================================

@app.route("/")
def home():
    return "Casino Bot is running!"


def run_flask():
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def get_user(user):

    user_id = user.id

    existing_user = users_collection.find_one(
        {"user_id": user_id}
    )

    if existing_user:

        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "name": user.first_name or "User",
                    "username": user.username or ""
                }
            }
        )

        return users_collection.find_one(
            {"user_id": user_id}
        )

    # FIRST TIME USER
    new_user = {
        "user_id": user_id,
        "name": user.first_name or "User",
        "username": user.username or "",
        "usd": WELCOME_USD,
        "dia": WELCOME_DIA,
        "welcome_bonus": True
    }

    users_collection.insert_one(new_user)

    return new_user


def find_user(user_id):

    return users_collection.find_one(
        {"user_id": user_id}
    )


def add_usd(user_id, amount):

    users_collection.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "usd": amount
            }
        }
    )


def remove_usd(user_id, amount):

    users_collection.update_one(
        {
            "user_id": user_id,
            "usd": {"$gte": amount}
        },
        {
            "$inc": {
                "usd": -amount
            }
        }
    )


def add_dia(user_id, amount):

    users_collection.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "dia": amount
            }
        }
    )


def money(number):

    return f"{number:,}"


def mention_user(user):

    name = user.first_name or "User"

    return (
        f'<a href="tg://user?id={user.id}">'
        f'{name}'
        f'</a>'
    )


def is_owner(user):

    if not user.username:
        return False

    return (
        user.username.lower()
        == OWNER_USERNAME.lower()
    )


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start_command(message):

    # Check if user existed BEFORE creating
    old_user = find_user(message.from_user.id)

    user = get_user(message.from_user)

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(
            "💰 Balance",
            callback_data=f"balance:{message.from_user.id}"
        ),
        types.InlineKeyboardButton(
            "🎰 Play Game",
            callback_data=f"game:{message.from_user.id}"
        )
    )

    # FIRST TIME BONUS
    if old_user is None:

        text = (
            "🎉 <b>WELCOME BONUS!</b> 🎉\n\n"

            f"👤 {mention_user(message.from_user)}\n\n"

            "🎁 သင့်ကို Free Bonus ပေးလိုက်ပါတယ်!\n\n"

            f"💵 USD ┃ ${money(WELCOME_USD)}\n"
            f"💎 DIA ┃ {money(WELCOME_DIA)} 💎\n\n"

            "━━━━━━━━━━━━━━━━━━━━\n\n"

            "⚠️ ဒီ Bonus ကို တစ်ကြိမ်တည်းသာ ရရှိနိုင်ပါတယ်!"
        )

    else:

        text = (
            "╔══════════════════════╗\n"
            "     🎰 CASINO BOT 🎰\n"
            "╚══════════════════════╝\n\n"

            f"👤 {mention_user(message.from_user)}\n\n"

            "🎮 Game ကစားရန်နှင့် Balance ကြည့်ရန်\n"
            "အောက်က Button ကိုရွေးပါ 👇"
        )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# BALANCE SCREEN
# =========================================================

def send_balance(chat_id, user_id, reply_message=None):

    user = find_user(user_id)

    if not user:
        return

    text = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "       💰 BALANCE 💰\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 {user['name']}\n\n"

        f"💵 USD ┃ ${money(user['usd'])}\n"
        f"💎 DIA ┃ {money(user['dia'])} 💎"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "💵 USD ဝယ်ယူရန်",
            callback_data=f"buy_usd_info:{user_id}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔄 Refresh Balance",
            callback_data=f"balance:{user_id}"
        )
    )

    if reply_message:

        bot.reply_to(
            reply_message,
            text,
            reply_markup=markup
        )

    else:

        bot.send_message(
            chat_id,
            text,
            reply_markup=markup
        )


@bot.message_handler(commands=["balance"])
def balance_command(message):

    get_user(message.from_user)

    send_balance(
        message.chat.id,
        message.from_user.id,
        message
    )


# =========================================================
# BALANCE BUTTON
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("balance:")
)
def balance_callback(call):

    owner_id = int(call.data.split(":")[1])

    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "🚫 ဒီ Balance က မင်းရဲ့ Balance မဟုတ်ပါ!",
            show_alert=True
        )

        return

    user = find_user(owner_id)

    text = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "       💰 BALANCE 💰\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 {user['name']}\n\n"

        f"💵 USD ┃ ${money(user['usd'])}\n"
        f"💎 DIA ┃ {money(user['dia'])} 💎"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "💵 USD ဝယ်ယူရန်",
            callback_data=f"buy_usd_info:{owner_id}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔄 Refresh Balance",
            callback_data=f"balance:{owner_id}"
        )
    )

    bot.answer_callback_query(call.id)

    try:
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception:
        pass


# =========================================================
# BUY USD INFORMATION
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("buy_usd_info:")
)
def buy_usd_info(call):

    owner_id = int(call.data.split(":")[1])

    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "🚫 ဒီခလုတ်ကို Balance ပိုင်ရှင်ပဲ သုံးနိုင်ပါတယ်!",
            show_alert=True
        )

        return

    bot.answer_callback_query(call.id)

    text = (
        "💵 <b>USD ဝယ်ရန်</b>\n\n"

        "💱 <b>လက်ရှိစျေးနှုန်း:</b> "
        "100 USD = 1 💎\n\n"

        "📌 <code>/buyusd [USD amount]</code> "
        "ဟုရိုက်ပြီး 💎 Star ဖြင့် USD ဝယ်နိုင်ပါတယ်။\n\n"

        "<i>Example:</i> <code>/buyusd 1</code>"
    )

    bot.send_message(
        call.message.chat.id,
        text,
        parse_mode="HTML"
    )


# =========================================================
# BUY USD COMMAND
# =========================================================

@bot.message_handler(commands=["buyusd"])
def buy_usd_command(message):

    text = (
        "💵 <b>USD ဝယ်ရန်</b>\n\n"

        "💱 <b>လက်ရှိစျေးနှုန်း:</b> "
        "100 USD = 1 💎\n\n"

        "📌 Telegram Stars Payment System ကို "
        "နောက်အဆင့်မှာ ချိတ်ဆက်နိုင်ပါတယ်။\n\n"

        "<i>Example:</i> "
        "<code>/buyusd 100</code>"
    )

    bot.reply_to(
        message,
        text,
        parse_mode="HTML"
    )


# =========================================================
# GAME COMMAND
# =========================================================

@bot.message_handler(commands=["game"])
def game_command(message):

    user = get_user(message.from_user)

    owner_id = message.from_user.id

    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "          🎰 CASINO 🎰\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 {mention_user(message.from_user)}\n\n"

        f"💵 ${money(user['usd'])}"
        "     "
        f"💎 {money(user['dia'])}\n\n"

        "🎰 SLOT MACHINE\n\n"

        "🍀 ကံစမ်းပြီး ဆုကြေးရယူပါ!"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🎰      PLAY SLOT MACHINE      🎰",
            callback_data=f"game_slot:{owner_id}"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# GAME BUTTON
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("game:")
)
def game_callback(call):

    owner_id = int(call.data.split(":")[1])

    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "🚫 ဒီ Casino က မင်းဖွင့်ထားတာမဟုတ်ပါ!\n\n"
            "🎰 ကိုယ်တိုင် /game ရိုက်ပြီး ကစားပါ။",
            show_alert=True
        )

        return

    user = get_user(call.from_user)

    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "          🎰 CASINO 🎰\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 {mention_user(call.from_user)}\n\n"

        f"💵 ${money(user['usd'])}"
        "     "
        f"💎 {money(user['dia'])}\n\n"

        "🎰 SLOT MACHINE\n\n"

        "🍀 ကံစမ်းပြီး ဆုကြေးရယူပါ!"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🎰      PLAY SLOT MACHINE      🎰",
            callback_data=f"game_slot:{owner_id}"
        )
    )

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# BET AMOUNTS
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

    return names.get(
        amount,
        f"{money(amount)} USD"
    )


def create_bet_keyboard(owner_id):

    markup = types.InlineKeyboardMarkup()

    # Large buttons
    for amount in BET_AMOUNTS:

        markup.add(
            types.InlineKeyboardButton(
                f"💵        {bet_name(amount)}        💵",
                callback_data=(
                    f"slot_bet:{owner_id}:{amount}"
                )
            )
        )

    return markup


# =========================================================
# PLAY SLOT
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("game_slot:")
)
def slot_screen(call):

    owner_id = int(call.data.split(":")[1])

    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "🚫 ဒီ Casino က မင်းဖွင့်ထားတာမဟုတ်ပါ!\n\n"
            "ကိုယ်တိုင် /game ရိုက်ပြီး ကစားပါ 🎰",
            show_alert=True
        )

        return

    user = get_user(call.from_user)

    bot.answer_callback_query(call.id)

    # DELETE OLD GAME SCREEN
    try:
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    except Exception:
        pass

    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🎰 SLOT MACHINE 🎰\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 {mention_user(call.from_user)}\n\n"

        f"💵 USD ┃ ${money(user['usd'])}\n"
        f"💎 DIA ┃ {money(user['dia'])} 💎\n\n"

        "🍇   🍋   7️⃣   BAR\n\n"

        "🏆 777 → 30×\n"
        "🏆 BAR BAR BAR → 10×\n"
        "🏆 77🍇 / 🍇77 / 77BAR → 3×\n"
        "🏆 🍇🍇🍇 / 🍋🍋🍋 → 5×\n\n"

        "💰 လောင်းကြေးရွေးပါ 👇"
    )

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=create_bet_keyboard(owner_id),
        parse_mode="HTML"
    )


# =========================================================
# SLOT DECODER
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
# SLOT PAYOUT
# =========================================================

def get_slot_payout(dice_value):

    left, middle, right = get_slot_combination(
        dice_value
    )

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

    # 77 GRAPE = 3x
    if (
        left == "7️⃣"
        and middle == "7️⃣"
        and right == "🍇"
    ):
        return 3

    # GRAPE 77 = 3x
    if (
        left == "🍇"
        and middle == "7️⃣"
        and right == "7️⃣"
    ):
        return 3

    # 77 BAR = 3x
    if (
        left == "7️⃣"
        and middle == "7️⃣"
        and right == "BAR"
    ):
        return 3

    # Three identical fruits = 5x
    if left == middle == right:

        if left in ["🍇", "🍋"]:
            return 5

    return 0


# =========================================================
# SLOT RESULT
# =========================================================

def send_slot_result(
    dice_message,
    telegram_user,
    bet,
    multiplier,
    dice_value,
    owner_id
):

    left, middle, right = get_slot_combination(
        dice_value
    )

    combination = (
        f"{left}   {middle}   {right}"
    )

    user = find_user(telegram_user.id)

    if multiplier > 0:

        winnings = bet * multiplier

        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "      🎰 SLOT RESULT 🎰\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"

            f"👤 {mention_user(telegram_user)}\n\n"

            f"🎰 {combination}\n\n"

            "🎉 ဒီတစ်ခါ နိုင်ပါတယ်!\n\n"

            f"🏆 {multiplier}× WIN\n"
            f"💰 အနိုင်ရငွေ ┃ ${money(winnings)}\n\n"

            f"💵 USD ┃ ${money(user['usd'])}\n"
            f"💎 DIA ┃ {money(user['dia'])} 💎\n\n"

            "💰 နောက်ထပ် လောင်းကြေးရွေးပါ 👇"
        )

    else:

        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "      🎰 SLOT RESULT 🎰\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"

            f"👤 {mention_user(telegram_user)}\n\n"

            f"🎰 {combination}\n\n"

            "😢 ဒီတစ်ခါ ရှုံးသွားပါတယ်။\n\n"

            f"💸 ရှုံးကြေး ┃ ${money(bet)}\n\n"

            f"💵 USD ┃ ${money(user['usd'])}\n"
            f"💎 DIA ┃ {money(user['dia'])} 💎\n\n"

            "💰 နောက်ထပ် လောင်းကြေးရွေးပါ 👇"
        )

    bot.reply_to(
        dice_message,
        text,
        reply_markup=create_bet_keyboard(owner_id),
        parse_mode="HTML"
    )


# =========================================================
# SLOT BET
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("slot_bet:")
)
def slot_bet(call):

    try:

        parts = call.data.split(":")

        owner_id = int(parts[1])
        bet = int(parts[2])

    except Exception:

        bot.answer_callback_query(
            call.id,
            "❌ Error!"
        )

        return

    # OWNER ONLY
    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "🚫 ဒီ Casino က မင်းဖွင့်ထားတာမဟုတ်ပါ!\n\n"
            "ကိုယ်တိုင် /game ရိုက်ပြီး ကစားပါ 🎰",
            show_alert=True
        )

        return

    if bet not in BET_AMOUNTS:

        bot.answer_callback_query(
            call.id,
            "❌ Invalid Bet!"
        )

        return

    user = get_user(call.from_user)

    # BALANCE CHECK
    if user["usd"] < bet:

        bot.answer_callback_query(
            call.id,
            "❌ USD Balance မလုံလောက်ပါ!",
            show_alert=True
        )

        return

    # REMOVE BET
    remove_usd(
        call.from_user.id,
        bet
    )

    bot.answer_callback_query(
        call.id,
        "🎰 Good Luck! 🍀"
    )

    # REAL TELEGRAM SLOT
    dice_message = bot.send_dice(
        call.message.chat.id,
        emoji="🎰"
    )

    # WAIT FOR SLOT ANIMATION
    time.sleep(4)

    dice_value = dice_message.dice.value

    multiplier = get_slot_payout(
        dice_value
    )

    # ADD WINNINGS
    if multiplier > 0:

        winnings = bet * multiplier

        add_usd(
            call.from_user.id,
            winnings
        )

    send_slot_result(
        dice_message,
        call.from_user,
        bet,
        multiplier,
        dice_value,
        owner_id
    )


# =========================================================
# GIFT KEYBOARD
# =========================================================

def gift_keyboard(
    gift_type,
    target_id,
    amount,
    owner_id
):

    markup = types.InlineKeyboardMarkup()

    markup.row(

        types.InlineKeyboardButton(
            "✅ CONFIRM",
            callback_data=(
                f"gift_confirm:"
                f"{gift_type}:"
                f"{target_id}:"
                f"{amount}:"
                f"{owner_id}"
            )
        ),

        types.InlineKeyboardButton(
            "❌ CANCEL",
            callback_data=(
                f"gift_cancel:{owner_id}"
            )
        )
    )

    return markup


# =========================================================
# GIFT USD
# =========================================================

@bot.message_handler(commands=["gift"])
def gift_command(message):

    if not is_owner(message.from_user):

        bot.reply_to(
            message,
            "❌ Owner only!"
        )

        return

    if not message.reply_to_message:

        bot.reply_to(
            message,
            "အသုံးပြုပုံ:\n\n"
            "User message ကို Reply လုပ်ပြီး\n"
            "/gift 100"
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "❌ Amount ထည့်ပါ။"
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

    if amount <= 0:

        bot.reply_to(
            message,
            "❌ Amount မမှန်ပါ။"
        )

        return

    target = message.reply_to_message.from_user

    get_user(target)

    text = (
        "🎁 USD GIFT CONFIRM\n\n"

        f"👤 {mention_user(target)}\n\n"

        f"💵 Amount ┃ ${money(amount)} USD\n\n"

        "ဒီ Gift ကို ပေးမှာသေချာပါသလား?"
    )

    bot.reply_to(
        message,
        text,
        reply_markup=gift_keyboard(
            "usd",
            target.id,
            amount,
            message.from_user.id
        ),
        parse_mode="HTML"
    )


# =========================================================
# GIFT DIA
# =========================================================

@bot.message_handler(commands=["giftdia"])
def gift_dia_command(message):

    if not is_owner(message.from_user):

        bot.reply_to(
            message,
            "❌ Owner only!"
        )

        return

    if not message.reply_to_message:

        bot.reply_to(
            message,
            "အသုံးပြုပုံ:\n\n"
            "User message ကို Reply လုပ်ပြီး\n"
            "/giftdia 100"
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "❌ Amount ထည့်ပါ။"
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

    if amount <= 0:

        bot.reply_to(
            message,
            "❌ Amount မမှန်ပါ။"
        )

        return

    target = message.reply_to_message.from_user

    get_user(target)

    text = (
        "🎁 DIA GIFT CONFIRM\n\n"

        f"👤 {mention_user(target)}\n\n"

        f"💎 Amount ┃ {money(amount)} DIA\n\n"

        "ဒီ Gift ကို ပေးမှာသေချာပါသလား?"
    )

    bot.reply_to(
        message,
        text,
        reply_markup=gift_keyboard(
            "dia",
            target.id,
            amount,
            message.from_user.id
        ),
        parse_mode="HTML"
    )


# =========================================================
# GIFT CONFIRM
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("gift_confirm:")
)
def gift_confirm(call):

    try:

        parts = call.data.split(":")

        gift_type = parts[1]
        target_id = int(parts[2])
        amount = int(parts[3])
        owner_id = int(parts[4])

    except Exception:

        bot.answer_callback_query(
            call.id,
            "❌ Error!"
        )

        return

    # OWNER ONLY
    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "🚫 ဒီ Gift ကိုဖန်တီးတဲ့သူပဲ Confirm လုပ်နိုင်ပါတယ်!",
            show_alert=True
        )

        return

    target = find_user(target_id)

    if not target:

        bot.answer_callback_query(
            call.id,
            "❌ User မတွေ့ပါ!"
        )

        return

    if gift_type == "usd":

        add_usd(
            target_id,
            amount
        )

        target = find_user(target_id)

        result = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "     🎁 GIFT SUCCESS\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"

            f"👤 {target['name']}\n\n"

            f"💵 +${money(amount)} USD\n\n"

            f"💰 Balance ┃ "
            f"${money(target['usd'])}"
        )

    else:

        add_dia(
            target_id,
            amount
        )

        target = find_user(target_id)

        result = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "     🎁 GIFT SUCCESS\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"

            f"👤 {target['name']}\n\n"

            f"💎 +{money(amount)} DIA\n\n"

            f"💎 Balance ┃ "
            f"{money(target['dia'])}"
        )

    bot.answer_callback_query(
        call.id,
        "✅ Gift ပေးပြီးပါပြီ!"
    )

    bot.edit_message_text(
        result,
        call.message.chat.id,
        call.message.message_id
    )


# =========================================================
# GIFT CANCEL
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("gift_cancel:")
)
def gift_cancel(call):

    owner_id = int(
        call.data.split(":")[1]
    )

    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "🚫 Gift ဖန်တီးတဲ့သူပဲ Cancel လုပ်နိုင်ပါတယ်!",
            show_alert=True
        )

        return

    bot.answer_callback_query(
        call.id,
        "❌ Gift Cancelled!"
    )

    bot.edit_message_text(
        "❌ Gift လုပ်ဆောင်မှုကို ပယ်ဖျက်လိုက်ပါပြီ။",
        call.message.chat.id,
        call.message.message_id
    )


# =========================================================
# OWNER USD ADD
# =========================================================

@bot.message_handler(commands=["usd"])
def usd_command(message):

    if not is_owner(message.from_user):

        bot.reply_to(
            message,
            "❌ Owner only!"
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "/usd 100"
        )

        return

    try:
        amount = int(parts[1])

    except ValueError:

        bot.reply_to(
            message,
            "❌ Invalid amount!"
        )

        return

    get_user(message.from_user)

    add_usd(
        message.from_user.id,
        amount
    )

    user = find_user(
        message.from_user.id
    )

    bot.reply_to(
        message,
        f"✅ ${money(amount)} USD Added!\n\n"
        f"💵 Balance ┃ ${money(user['usd'])}"
    )


# =========================================================
# OWNER DIA ADD
# =========================================================

@bot.message_handler(commands=["dia"])
def dia_command(message):

    if not is_owner(message.from_user):

        bot.reply_to(
            message,
            "❌ Owner only!"
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "/dia 100"
        )

        return

    try:
        amount = int(parts[1])

    except ValueError:

        bot.reply_to(
            message,
            "❌ Invalid amount!"
        )

        return

    get_user(message.from_user)

    add_dia(
        message.from_user.id,
        amount
    )

    user = find_user(
        message.from_user.id
    )

    bot.reply_to(
        message,
        f"✅ {money(amount)} DIA Added!\n\n"
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
            "balance",
            "Balance ကြည့်ရန်"
        ),

        types.BotCommand(
            "game",
            "Casino Game ကစားရန်"
        ),

        types.BotCommand(
            "buyusd",
            "USD ဝယ်ယူရန်"
        )
    ]

    bot.set_my_commands(commands)


# =========================================================
# START BOT
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
