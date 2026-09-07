import os
import time
import threading
import uuid

import telebot
from telebot import types
from flask import Flask
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError


# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set")

bot = telebot.TeleBot(BOT_TOKEN)

OWNER_USERNAME = "Ruifineshyt"

app = Flask(__name__)


# =========================================================
# FLASK
# =========================================================

@app.route("/")
def home():
    return "Bot is running!"


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# =========================================================
# MONGODB
# =========================================================

mongo_client = MongoClient(MONGO_URI)

db = mongo_client["casino_bot"]

users_collection = db["users"]

users_collection.create_index(
    [("user_id", ASCENDING)],
    unique=True
)


# =========================================================
# HELPERS
# =========================================================

def money(value):
    return f"{int(value):,}"


def mention_user(user):
    name = user.first_name or "User"
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def is_owner(message):
    username = message.from_user.username

    if not username:
        return False

    return username.lower() == OWNER_USERNAME.lower()


def get_user(user):
    user_id = user.id

    existing = users_collection.find_one({
        "user_id": user_id
    })

    if existing:
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "name": user.first_name or "User",
                    "username": user.username or ""
                }
            }
        )

        existing["name"] = user.first_name or "User"
        existing["username"] = user.username or ""

        return existing

    new_user = {
        "user_id": user_id,
        "name": user.first_name or "User",
        "username": user.username or "",
        "usd": 20000,
        "dia": 500,
        "welcome_bonus": True
    }

    try:
        users_collection.insert_one(new_user)
        return new_user

    except DuplicateKeyError:
        return users_collection.find_one({
            "user_id": user_id
        })


def update_balance(user_id, usd_change=0, dia_change=0):
    users_collection.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "usd": usd_change,
                "dia": dia_change
            }
        }
    )


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start_command(message):

    user = get_user(message.from_user)

    text = (
        f"👋 မင်္ဂလာပါ {mention_user(message.from_user)}!\n\n"
        "🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!\n\n"
        f"💎 Diamonds: {money(user.get('dia', 0))}💎\n"
        f"💵 USD: ${money(user.get('usd', 0))}USD\n\n"
        "🎁 ပထမဆုံးအကြိမ်အသုံးပြုသူများအတွက်\n"
        "💵 $20,000 USD\n"
        "💎 500 DIA\n"
        "အခမဲ့ရရှိပါတယ်။\n\n"
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

    user = get_user(message.from_user)

    text = (
        f"👤 {mention_user(message.from_user)}\n\n"
        "💰 YOUR BALANCE\n\n"
        f"💵 USD ┃ ${money(user.get('usd', 0))}\n"
        f"💎 DIA ┃ {money(user.get('dia', 0))}💎"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "💵 USD ဝယ်ယူရန်",
            callback_data="buy_usd_info"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# USD BUY BUTTON
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "buy_usd_info"
)
def buy_usd_info(call):

    bot.answer_callback_query(call.id)

    text = (
        "💵 <b>USD ဝယ်ရန်</b>\n\n"
        "💱 <b>လက်ရှိစျေးနှုန်း:</b> 100 USD = 1💎\n\n"
        "📌 <code>/buyusd [USD amount]</code> "
        "ဟုရိုက်ပြီး 💎 DIA ဖြင့် USD ဝယ်နိုင်ပါတယ်။\n\n"
        "<i>Example:</i> <code>/buyusd 100</code>"
    )

    bot.send_message(
        call.message.chat.id,
        text,
        parse_mode="HTML"
    )


# =========================================================
# BUY USD
# 100 USD = 1 DIA
# =========================================================

@bot.message_handler(commands=["buyusd"])
def buyusd_command(message):

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "❌ USD amount ထည့်ပါ။\n\n"
            "အသုံးပြုပုံ:\n"
            "/buyusd 100"
        )

        return

    try:
        usd_amount = int(parts[1])
    except ValueError:

        bot.reply_to(
            message,
            "❌ USD amount မမှန်ပါ။"
        )

        return

    if usd_amount <= 0:

        bot.reply_to(
            message,
            "❌ Amount က 0 ထက်ကြီးရပါမယ်။"
        )

        return

    # Must be multiple of 100
    if usd_amount % 100 != 0:

        bot.reply_to(
            message,
            "❌ USD amount ကို 100 ရဲ့ ဆတိုးပမာဏနဲ့ပဲ ဝယ်နိုင်ပါတယ်။\n\n"
            "ဥပမာ - /buyusd 100\n"
            "ဥပမာ - /buyusd 500"
        )

        return

    dia_needed = usd_amount // 100

    user = get_user(message.from_user)

    if user.get("dia", 0) < dia_needed:

        bot.reply_to(
            message,
            "❌ DIA မလုံလောက်ပါ။\n\n"
            f"💎 လိုအပ်သော DIA — {money(dia_needed)}💎\n"
            f"💎 လက်ရှိ DIA — {money(user.get('dia', 0))}💎"
        )

        return

    update_balance(
        message.from_user.id,
        usd_change=usd_amount,
        dia_change=-dia_needed
    )

    new_user = get_user(message.from_user)

    bot.reply_to(
        message,
        "✅ <b>USD ဝယ်ယူပြီးပါပြီ!</b>\n\n"
        f"💵 +${money(usd_amount)} USD\n"
        f"💎 -{money(dia_needed)} DIA\n\n"
        "💰 လက်ရှိ Balance\n"
        f"💵 USD ┃ ${money(new_user.get('usd', 0))}\n"
        f"💎 DIA ┃ {money(new_user.get('dia', 0))}💎",
        parse_mode="HTML"
    )


# =========================================================
# GAME
# =========================================================

@bot.message_handler(commands=["game"])
def game_command(message):

    user = get_user(message.from_user)

    text = (
        "╔════════════════════════════╗\n"
        "        🎰 CASINO 🎰\n"
        "╚════════════════════════════╝\n\n"
        f"👤 {mention_user(message.from_user)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 YOUR BALANCE\n"
        f"💵 USD   ┃  ${money(user.get('usd', 0))}\n"
        f"💎 DIA   ┃  {money(user.get('dia', 0))}💎\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎮 GAME CENTER\n\n"
        "🎰 SLOT MACHINE\n"
        "🍀 သင့်ကံကို စမ်းသပ်ပါ!\n"
        "💰 လောင်းကြေးရွေးပြီး စတင်ကစားပါ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ ဒီ Game ကို ဖော်ထားတဲ့သူက\n"
        "သူကိုယ်တိုင်ပဲ ကစားနိုင်ပါတယ်။\n\n"
        "👇 PLAY NOW 👇"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🎰 PLAY SLOT MACHINE 🎰",
            callback_data=f"game_slot:{message.from_user.id}"
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
# 3 x 3
# =========================================================

def create_bet_keyboard():

    markup = types.InlineKeyboardMarkup()

    # Row 1
    markup.row(
        types.InlineKeyboardButton(
            "💵 10 USD",
            callback_data="slot_bet:10"
        ),
        types.InlineKeyboardButton(
            "💵 100 USD",
            callback_data="slot_bet:100"
        ),
        types.InlineKeyboardButton(
            "💵 1K USD",
            callback_data="slot_bet:1000"
        )
    )

    # Row 2
    markup.row(
        types.InlineKeyboardButton(
            "💵 5K USD",
            callback_data="slot_bet:5000"
        ),
        types.InlineKeyboardButton(
            "💵 10K USD",
            callback_data="slot_bet:10000"
        ),
        types.InlineKeyboardButton(
            "💵 100K USD",
            callback_data="slot_bet:100000"
        )
    )

    # Row 3
    markup.row(
        types.InlineKeyboardButton(
            "💵 300K USD",
            callback_data="slot_bet:300000"
        ),
        types.InlineKeyboardButton(
            "💵 500K USD",
            callback_data="slot_bet:500000"
        ),
        types.InlineKeyboardButton(
            "💵 1M USD",
            callback_data="slot_bet:1000000"
        )
    )

    return markup


# =========================================================
# PLAY SLOT
# DELETE OLD GAME MESSAGE
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("game_slot:")
)
def slot_button(call):

    try:
        owner_id = int(
            call.data.split(":")[1]
        )
    except Exception:

        bot.answer_callback_query(
            call.id,
            "❌ Game error."
        )

        return

    # Only creator can play
    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "⚠️ ဒီ Game က သင့် Game မဟုတ်ပါဘူး။\n\n"
            "/game ကို ကိုယ်တိုင်ဖော်ပါ။",
            show_alert=True
        )

        return

    user = get_user(call.from_user)

    bot.answer_callback_query(call.id)

    # DELETE OLD GAME CENTER
    try:

        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )

    except Exception:
        pass

    # NEW BET SCREEN
    text = (
        "╔════════════════════════════╗\n"
        "        🎰 SLOT MACHINE 🎰\n"
        "╚════════════════════════════╝\n\n"
        f"👤 {mention_user(call.from_user)}\n\n"
        "💰 YOUR BALANCE\n"
        f"💵 USD ┃ ${money(user.get('usd', 0))}\n"
        f"💎 DIA ┃ {money(user.get('dia', 0))}💎\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💵 လောင်းကြေးရွေးပါ 👇"
    )

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=create_bet_keyboard(),
        parse_mode="HTML"
    )


# =========================================================
# SLOT COMBINATION
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

    # 77 BAR = 3x
    if (
        left == "7️⃣"
        and middle == "7️⃣"
        and right == "BAR"
    ):
        return 3

    # 7🍇7 = loss
    if (
        left == "7️⃣"
        and middle == "🍇"
        and right == "7️⃣"
    ):
        return 0

    # Three identical fruits = 5x
    if left == middle == right:

        if left in ["🍇", "🍋"]:
            return 5

    # Everything else = loss
    return 0


# =========================================================
# SLOT RESULT
# =========================================================

def send_slot_result(
    dice_message,
    telegram_user,
    bet,
    multiplier,
    dice_value
):

    current_user = get_user(
        telegram_user
    )

    left, middle, right = get_slot_combination(
        dice_value
    )

    combination = (
        f"{left}  {middle}  {right}"
    )

    if multiplier > 0:

        winnings = bet * multiplier

        result_text = (
            f"🎰 {mention_user(telegram_user)}\n\n"
            f"🎰 {combination}\n\n"
            "🎉 <b>ဒီတစ်ခါ နိုင်ပါတယ်!</b>\n"
            f"🏆 ဆုကြေး — <b>{multiplier}×</b>\n"
            f"💰 အနိုင်ရငွေ — <b>${money(winnings)} USD</b>\n\n"
            "🍀 နောက်တစ်ကြိမ်လည်း ကံကောင်းပါစေ!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💰 လက်ရှိ Balance\n"
            f"💵 USD ┃ ${money(current_user.get('usd', 0))}\n"
            f"💎 DIA ┃ {money(current_user.get('dia', 0))}💎\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💵 နောက်တစ်ကြိမ် ထိုးမယ့် လောင်းကြေးရွေးပါ 👇"
        )

    else:

        result_text = (
            f"🎰 {mention_user(telegram_user)}\n\n"
            f"🎰 {combination}\n\n"
            "😢 <b>ဒီတစ်ခါ ရှုံးသွားပါတယ်။</b>\n"
            f"💸 ရှုံးကြေး — <b>${money(bet)} USD</b>\n\n"
            "🍀 နောက်တစ်ကြိမ် ကံကောင်းပါစေ!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💰 လက်ရှိ Balance\n"
            f"💵 USD ┃ ${money(current_user.get('usd', 0))}\n"
            f"💎 DIA ┃ {money(current_user.get('dia', 0))}💎\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💵 နောက်တစ်ကြိမ် ထိုးမယ့် လောင်းကြေးရွေးပါ 👇"
        )

    # Reply to dice animation
    bot.reply_to(
        dice_message,
        result_text,
        reply_markup=create_bet_keyboard(),
        parse_mode="HTML"
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
        call.from_user
    )

    # Balance check
    if user.get("usd", 0) < bet:

        bot.answer_callback_query(
            call.id,
            "❌ Balance မလုံလောက်ပါ!",
            show_alert=True
        )

        return

    # Deduct bet
    update_balance(
        call.from_user.id,
        usd_change=-bet
    )

    bot.answer_callback_query(call.id)

    # Telegram native slot
    dice_msg = bot.send_dice(
        call.message.chat.id,
        emoji="🎰"
    )

    # Wait for animation
    time.sleep(4)

    dice_value = dice_msg.dice.value

    multiplier = get_slot_payout(
        dice_value
    )

    # Add winnings
    if multiplier > 0:

        winnings = bet * multiplier

        update_balance(
            call.from_user.id,
            usd_change=winnings
        )

    send_slot_result(
        dice_msg,
        call.from_user,
        bet,
        multiplier,
        dice_value
    )


# =========================================================
# /USD
# OWNER ONLY
# NOT IN MENU
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
            "အသုံးပြုပုံ\n\n"
            "/usd 100"
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
            "❌ Amount မှန်မှန်ထည့်ပါ။"
        )

        return

    get_user(message.from_user)

    update_balance(
        message.from_user.id,
        usd_change=amount
    )

    new_user = get_user(
        message.from_user
    )

    bot.reply_to(
        message,
        f"✅ USD ${money(amount)} ထည့်ပြီးပါပြီ။\n\n"
        f"💵 Balance ┃ ${money(new_user.get('usd', 0))}"
    )


# =========================================================
# /DIA
# OWNER ONLY
# NOT IN MENU
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
            "အသုံးပြုပုံ\n\n"
            "/dia 100"
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
            "❌ Amount မှန်မှန်ထည့်ပါ။"
        )

        return

    get_user(message.from_user)

    update_balance(
        message.from_user.id,
        dia_change=amount
    )

    new_user = get_user(
        message.from_user
    )

    bot.reply_to(
        message,
        f"✅ Diamonds {money(amount)}💎 ထည့်ပြီးပါပြီ။\n\n"
        f"💎 Balance ┃ {money(new_user.get('dia', 0))}💎"
    )


# =========================================================
# PENDING GIFTS
# =========================================================

pending_gifts = {}


# =========================================================
# /GIFTUSD
# PUBLIC
# IN MENU
# =========================================================

@bot.message_handler(commands=["giftusd"])
def giftusd_command(message):

    if not message.reply_to_message:

        bot.reply_to(
            message,
            "❌ User ရဲ့ message ကို Reply လုပ်ပြီး\n\n"
            "/giftusd amount\n\n"
            "ဥပမာ - /giftusd 100"
        )

        return

    parts = message.text.split()

    if len(parts) < 2:

        bot.reply_to(
            message,
            "❌ Amount ထည့်ပါ။\n\n"
            "ဥပမာ - /giftusd 100"
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
            "❌ Amount က 0 ထက်ကြီးရပါမယ်။"
        )

        return

    target = message.reply_to_message.from_user

    if target.is_bot:

        bot.reply_to(
            message,
            "❌ Bot ကို Gift မပေးနိုင်ပါ။"
        )

        return

    get_user(target)

    gift_id = str(uuid.uuid4())

    pending_gifts[gift_id] = {
        "type": "usd",
        "amount": amount,
        "target_id": target.id,
        "target_name": target.first_name or "User"
    }

    text = (
        "🎁 <b>USD Gift အတည်ပြုရန်</b>\n\n"
        f"👤 လက်ခံသူ — {mention_user(target)}\n"
        f"💵 ပမာဏ — <b>${money(amount)} USD</b>\n\n"
        "ဒီ Gift ကို ပေးမည်မှာ သေချာပါသလား?"
    )

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(
            "✅ Confirm",
            callback_data=f"gift_confirm:{gift_id}"
        ),
        types.InlineKeyboardButton(
            "❌ Cancel",
            callback_data=f"gift_cancel:{gift_id}"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# /GIFTDIA
# PUBLIC
# IN MENU
# =========================================================

@bot.message_handler(commands=["giftdia"])
def giftdia_command(message):

    if not message.reply_to_message:

        bot.reply_to(
            message,
            "❌ User ရဲ့ message ကို Reply လုပ်ပြီး\n\n"
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

    if amount <= 0:

        bot.reply_to(
            message,
            "❌ Amount က 0 ထက်ကြီးရပါမယ်။"
        )

        return

    target = message.reply_to_message.from_user

    if target.is_bot:

        bot.reply_to(
            message,
            "❌ Bot ကို Gift မပေးနိုင်ပါ။"
        )

        return

    get_user(target)

    gift_id = str(uuid.uuid4())

    pending_gifts[gift_id] = {
        "type": "dia",
        "amount": amount,
        "target_id": target.id,
        "target_name": target.first_name or "User"
    }

    text = (
        "🎁 <b>DIA Gift အတည်ပြုရန်</b>\n\n"
        f"👤 လက်ခံသူ — {mention_user(target)}\n"
        f"💎 ပမာဏ — <b>{money(amount)} DIA</b>\n\n"
        "ဒီ Gift ကို ပေးမည်မှာ သေချာပါသလား?"
    )

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(
            "✅ Confirm",
            callback_data=f"gift_confirm:{gift_id}"
        ),
        types.InlineKeyboardButton(
            "❌ Cancel",
            callback_data=f"gift_cancel:{gift_id}"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# GIFT CONFIRM
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("gift_confirm:")
)
def gift_confirm(call):

    gift_id = call.data.split(
        ":",
        1
    )[1]

    gift = pending_gifts.get(
        gift_id
    )

    if not gift:

        bot.answer_callback_query(
            call.id,
            "❌ ဒီ Gift က မရှိတော့ပါဘူး။",
            show_alert=True
        )

        return

    amount = gift["amount"]
    target_id = gift["target_id"]
    target_name = gift["target_name"]

    if gift["type"] == "usd":

        update_balance(
            target_id,
            usd_change=amount
        )

        result_text = (
            "🎁 <b>USD Gift ပေးပြီးပါပြီ!</b>\n\n"
            f"👤 {target_name}\n"
            f"💵 +${money(amount)} USD"
        )

    else:

        update_balance(
            target_id,
            dia_change=amount
        )

        result_text = (
            "🎁 <b>Diamonds Gift ပေးပြီးပါပြီ!</b>\n\n"
            f"👤 {target_name}\n"
            f"💎 +{money(amount)} DIA"
        )

    del pending_gifts[gift_id]

    bot.answer_callback_query(
        call.id,
        "✅ Gift ပေးပြီးပါပြီ!"
    )

    try:

        bot.edit_message_text(
            result_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

    except Exception:
        pass


# =========================================================
# GIFT CANCEL
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("gift_cancel:")
)
def gift_cancel(call):

    gift_id = call.data.split(
        ":",
        1
    )[1]

    if gift_id in pending_gifts:
        del pending_gifts[gift_id]

    bot.answer_callback_query(
        call.id,
        "❌ Gift Cancel လုပ်ပြီးပါပြီ။"
    )

    try:

        bot.edit_message_text(
            "❌ <b>Gift Cancel လုပ်ပြီးပါပြီ။</b>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

    except Exception:
        pass


# =========================================================
# COMMAND MENU
#
# /giftusd and /giftdia ARE INCLUDED
#
# /usd and /dia are NOT included
# /buyusd is NOT included
# /gift does not exist
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
            "Game ကစားရန်"
        ),
        types.BotCommand(
            "giftusd",
            "USD Gift ပေးရန်"
        ),
        types.BotCommand(
            "giftdia",
            "Diamond Gift ပေးရန်"
        )
    ]

    bot.set_my_commands(commands)


# =========================================================
# UNKNOWN SLASH COMMANDS
#
# Bot မှာ မရှိတဲ့ /command တွေကို
# ဘာမှမပြန်ဘူး
# =========================================================

@bot.message_handler(
    func=lambda message: (
        message.text is not None
        and message.text.startswith("/")
    )
)
def unknown_command(message):
    return


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
