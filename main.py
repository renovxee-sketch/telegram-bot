import os
import random
import time
import html
import telebot

from flask import Flask
from threading import Thread
from pymongo import MongoClient
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==================================================
# CONFIG
# ==================================================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB", "telegram_game_bot")

OWNER_USERNAME = "Ruifineshyt"

if not TOKEN:
    raise RuntimeError("BOT_TOKEN မတွေ့ပါ။")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI မတွေ့ပါ။")


bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# ==================================================
# MONGODB
# ==================================================

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db["users"]


def get_user(user_id, first_name=None):

    user_id = int(user_id)

    user = users_collection.find_one({
        "_id": user_id
    })

    if not user:

        user = {
            "_id": user_id,
            "usd": 0,
            "dia": 0,
            "name": first_name or "Player"
        }

        users_collection.insert_one(user)

    else:

        if first_name:
            users_collection.update_one(
                {"_id": user_id},
                {"$set": {"name": first_name}}
            )

    return users_collection.find_one({
        "_id": user_id
    })


def update_balance(user_id, usd_change=0, dia_change=0):

    users_collection.update_one(
        {"_id": int(user_id)},
        {
            "$inc": {
                "usd": usd_change,
                "dia": dia_change
            }
        },
        upsert=True
    )


def is_owner(message):

    username = message.from_user.username

    if username:
        return username.lower() == OWNER_USERNAME.lower()

    return False


# ==================================================
# BOT MENU
# ==================================================

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
            "Game Menu"
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
        ),

        telebot.types.BotCommand(
            "giftdia",
            "Gift Diamonds"
        )
    ]

    bot.set_my_commands(commands)


# ==================================================
# START
# ==================================================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(
        user_id,
        user_name
    )

    safe_name = html.escape(user_name)

    text = (
        f'👋 မင်္ဂလာပါ '
        f'<a href="tg://user?id={user_id}">{safe_name}</a>!\n\n'
        '🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်!\n\n'
        f'💎 Diamonds: {user["dia"]:,}\n'
        f'💵 USD: ${user["usd"]:,}\n\n'
        '👇 အောက်ပါ Button ကို နှိပ်ပြီး '
        'သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!'
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


# ==================================================
# BALANCE
# ==================================================

@bot.message_handler(commands=["balance"])
def balance(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(
        user_id,
        user_name
    )

    safe_name = html.escape(user_name)

    text = (
        f"👤 <b>{safe_name} ({user_id})</b> ၏ လက်ကျန်ငွေ\n"
        f"💎 Diamonds: <b>{user['dia']:,}</b>💎\n"
        f"💵 USD: <b>${user['usd']:,}USD</b>"
    )

    bot.reply_to(
        message,
        text,
        parse_mode="HTML"
    )


# ==================================================
# GAME MENU
# ==================================================

@bot.message_handler(commands=["game"])
def game(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    safe_name = html.escape(user_name)

    text = (
        f'👋 <a href="tg://user?id={user_id}">{safe_name}</a> ရေ!\n\n'
        '🎮 <b>ဆော့ကစားနိုင်သောဂိမ်းများ</b>\n\n'
        '🎰 <b>SLOT MACHINE</b>\n'
        '💵 လောင်းကြေးရွေးပြီး ကစားနိုင်ပါတယ်။'
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "🎰 Slot",
            callback_data="slot_menu"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# SLOT MENU
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "slot_menu"
)
def slot_menu(call):

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "💵 10",
            callback_data="bet_10"
        ),
        InlineKeyboardButton(
            "💵 100",
            callback_data="bet_100"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            "💵 1K",
            callback_data="bet_1000"
        ),
        InlineKeyboardButton(
            "💵 10K",
            callback_data="bet_10000"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            "💵 100K",
            callback_data="bet_100000"
        ),
        InlineKeyboardButton(
            "💵 300K",
            callback_data="bet_300000"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            "💵 500K",
            callback_data="bet_500000"
        ),
        InlineKeyboardButton(
            "💵 1M",
            callback_data="bet_1000000"
        )
    )

    bot.answer_callback_query(
        call.id
    )

    bot.edit_message_text(
        "🎰 <b>SLOT MACHINE</b>\n\n"
        "💵 လောင်းကြေးပမာဏကို ရွေးပါ။",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# SLOT SYMBOLS
# ==================================================

SLOT_SYMBOLS = [
    "🍒",
    "🍋",
    "🍊",
    "🍉",
    "🍇",
    "🥝",
    "🔔",
    "⭐",
    "BAR",
    "7"
]


# ==================================================
# SLOT RESULT
# ==================================================

def get_slot_result():

    # 777 = 30x
    if random.random() < 0.01:
        return ["7", "7", "7"], 30

    # BAR BAR BAR = 10x
    if random.random() < 0.02:
        return ["BAR", "BAR", "BAR"], 10

    # 77🍇 / 🍇77 = 3x
    if random.random() < 0.04:

        if random.choice([True, False]):
            return ["7", "7", "🍇"], 3

        return ["🍇", "7", "7"], 3

    # Other fruit x3 = 5x
    if random.random() < 0.08:

        fruit = random.choice([
            "🍒",
            "🍋",
            "🍊",
            "🍉",
            "🍇",
            "🥝"
        ])

        return [fruit, fruit, fruit], 5

    # Normal losing result
    result = random.choices(
        SLOT_SYMBOLS,
        k=3
    )

    # Prevent accidental winning combinations
    if result[0] == result[1] == result[2]:
        result[2] = random.choice(
            [x for x in SLOT_SYMBOLS if x != result[0]]
        )

    # Prevent 77🍇 / 🍇77 from normal random result
    if (
        result == ["7", "7", "🍇"]
        or result == ["🍇", "7", "7"]
    ):
        result[2] = "🍒"

    return result, 0


# ==================================================
# SLOT BET
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("bet_")
)
def slot_bet(call):

    try:
        amount = int(
            call.data.replace(
                "bet_",
                ""
            )
        )
    except ValueError:

        bot.answer_callback_query(
            call.id,
            "❌ လောင်းကြေးမှားနေပါတယ်။",
            show_alert=True
        )

        return

    user_id = call.from_user.id
    user_name = call.from_user.first_name or "Player"

    user = get_user(
        user_id,
        user_name
    )

    # Balance check
    if user["usd"] < amount:

        bot.answer_callback_query(
            call.id,
            "❌ လက်ကျန် USD မလုံလောက်ပါ။",
            show_alert=True
        )

        return

    # Deduct bet first
    update_balance(
        user_id,
        usd_change=-amount
    )

    bot.answer_callback_query(
        call.id,
        f"🎰 {amount:,} USD လောင်းထားပါတယ်!"
    )

    safe_name = html.escape(user_name)

    # ==================================================
    # SPINNING ANIMATION
    # ==================================================

    animation_frames = [
        "🎰 <b>SLOT MACHINE</b>\n\n"
        f"👤 {safe_name} · 💵 {amount:,} USD\n\n"
        "🔄 <b>လှည့်နေပါတယ်...</b>\n\n"
        "❓ │ ❓ │ ❓",

        "🎰 <b>SLOT MACHINE</b>\n\n"
        f"👤 {safe_name} · 💵 {amount:,} USD\n\n"
        "🔄 <b>လှည့်နေပါတယ်...</b>\n\n"
        "🍒 │ 🔔 │ 7️⃣",

        "🎰 <b>SLOT MACHINE</b>\n\n"
        f"👤 {safe_name} · 💵 {amount:,} USD\n\n"
        "🔄 <b>နောက်ဆုံးလှည့်နေပါတယ်...</b>\n\n"
        "BAR │ 🍇 │ ⭐"
    ]

    for frame in animation_frames:

        try:

            bot.edit_message_text(
                frame,
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )

            time.sleep(0.7)

        except Exception:
            pass

    # ==================================================
    # RESULT
    # ==================================================

    result, multiplier = get_slot_result()

    result_text = (
        f"{result[0]} │ {result[1]} │ {result[2]}"
    )

    if multiplier > 0:

        payout = amount * multiplier
        net_profit = payout - amount

        update_balance(
            user_id,
            usd_change=payout
        )

        if multiplier == 30:

            title = "🔥 JACKPOT! အကြီးအကျယ် ကံကောင်းသွားပြီ!"

        elif multiplier == 10:

            title = "🎉 BAR သုံးလုံးတူပြီး အနိုင်ရပြီ!"

        elif multiplier == 5:

            title = "🎊 အသီးသုံးလုံးတူပြီး အနိုင်ရပြီ!"

        else:

            title = "🎉 ကံကောင်းတယ်! ဆုရပြီ!"

        final_text = (
            "🎰 <b>SLOT MACHINE</b>\n"
            f"👤 {safe_name} · 💵 {amount:,} USD\n\n"
            f"<b>{result_text}</b>\n"
            f"🏆 <b>{title}</b>\n"
            f"💰 <b>{multiplier}x ဆုကြေး — {payout:,} USD</b>\n"
            f"📈 <b>အသားတင်: +{net_profit:,} USD</b>"
        )

    else:

        final_text = (
            "🎰 <b>SLOT MACHINE</b>\n"
            f"👤 {safe_name} · 💵 {amount:,} USD\n\n"
            f"<b>{result_text}</b>\n"
            "💔 <b>ဒီတစ်ခါတော့ မကံကောင်းသေးဘူး!</b>\n"
            "😢 <b>ဆုမရပါ။</b>\n"
            f"📉 <b>အသားတင်: -{amount:,} USD</b>"
        )

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "🎰 ထပ်ကစားမယ်",
            callback_data="slot_menu"
        )
    )

    bot.edit_message_text(
        final_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# OWNER USD
# ==================================================

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
        message.from_user.id,
        message.from_user.first_name or "Player"
    )

    update_balance(
        message.from_user.id,
        usd_change=amount
    )

    new_balance = user["usd"] + amount

    bot.reply_to(
        message,
        f"✅ USD ထည့်ပြီးပါပြီ!\n\n"
        f"💵 +${amount:,}\n"
        f"💰 လက်ကျန်: ${new_balance:,}USD"
    )


# ==================================================
# OWNER DIAMOND
# ==================================================

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
        message.from_user.id,
        message.from_user.first_name or "Player"
    )

    update_balance(
        message.from_user.id,
        dia_change=amount
    )

    new_balance = user["dia"] + amount

    bot.reply_to(
        message,
        f"✅ Diamond ထည့်ပြီးပါပြီ!\n\n"
        f"💎 +{amount:,}\n"
        f"💎 လက်ကျန်: {new_balance:,} Diamonds"
    )


# ==================================================
# GIFT USD
# ==================================================

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

    target_name = target.first_name or "Player"

    get_user(
        target.id,
        target_name
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "✅ Confirm",
            callback_data=f"giftusd_confirm_{target.id}_{amount}"
        ),
        InlineKeyboardButton(
            "❌ Cancel",
            callback_data="giftusd_cancel"
        )
    )

    safe_target_name = html.escape(target_name)

    text = (
        "🎁 <b>USD Gift အတည်ပြုရန်</b>\n\n"
        f"👤 {safe_target_name}\n"
        f"💵 ပေးမည့်ပမာဏ: <b>{amount:,} USD</b>\n\n"
        "အတည်ပြုမယ်ဆိုရင် ✅ Confirm ကိုနှိပ်ပါ။"
    )

    bot.reply_to(
        message,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# CONFIRM GIFT USD
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("giftusd_confirm_")
)
def confirm_gift_usd(call):

    username = call.from_user.username

    if not username or username.lower() != OWNER_USERNAME.lower():

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

    except:

        bot.answer_callback_query(
            call.id,
            "❌ Error ဖြစ်သွားပါတယ်။",
            show_alert=True
        )

        return

    update_balance(
        target_id,
        usd_change=amount
    )

    bot.answer_callback_query(
        call.id,
        "✅ USD Gift ပေးပြီးပါပြီ!"
    )

    bot.edit_message_text(
        "🎁 <b>USD Gift ပေးပြီးပါပြီ!</b>\n\n"
        f"💵 +{amount:,} USD",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )


# ==================================================
# CANCEL GIFT USD
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "giftusd_cancel"
)
def cancel_gift_usd(call):

    username = call.from_user.username

    if not username or username.lower() != OWNER_USERNAME.lower():

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


# ==================================================
# GIFT DIAMOND
# ==================================================

@bot.message_handler(commands=["giftdia"])
def gift_dia(message):

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
            "❌ ဥပမာ - /giftdia 1000"
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

    target = message.reply_to_message.from_user

    target_name = target.first_name or "Player"

    get_user(
        target.id,
        target_name
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "✅ Confirm",
            callback_data=f"giftdia_confirm_{target.id}_{amount}"
        ),
        InlineKeyboardButton(
            "❌ Cancel",
            callback_data="giftdia_cancel"
        )
    )

    safe_target_name = html.escape(target_name)

    text = (
        "🎁 <b>Diamond Gift အတည်ပြုရန်</b>\n\n"
        f"👤 {safe_target_name}\n"
        f"💎 ပေးမည့်ပမာဏ: <b>{amount:,} Diamonds</b>\n\n"
        "အတည်ပြုမယ်ဆိုရင် ✅ Confirm ကိုနှိပ်ပါ။"
    )

    bot.reply_to(
        message,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# CONFIRM GIFT DIAMOND
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("giftdia_confirm_")
)
def confirm_gift_dia(call):

    username = call.from_user.username

    if not username or username.lower() != OWNER_USERNAME.lower():

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

    except:

        bot.answer_callback_query(
            call.id,
            "❌ Error ဖြစ်သွားပါတယ်။",
            show_alert=True
        )

        return

    update_balance(
        target_id,
        dia_change=amount
    )

    bot.answer_callback_query(
        call.id,
        "✅ Diamond Gift ပေးပြီးပါပြီ!"
    )

    bot.edit_message_text(
        "🎁 <b>Diamond Gift ပေးပြီးပါပြီ!</b>\n\n"
        f"💎 +{amount:,} Diamonds",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )


# ==================================================
# CANCEL GIFT DIAMOND
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "giftdia_cancel"
)
def cancel_gift_dia(call):

    username = call.from_user.username

    if not username or username.lower() != OWNER_USERNAME.lower():

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
        "❌ <b>Diamond Gift Cancel လုပ်ပြီးပါပြီ။</b>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )


# ==================================================
# FLASK
# ==================================================

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


# ==================================================
# START
# ==================================================

if __name__ == "__main__":

    set_commands()

    Thread(
        target=run
    ).start()

    print("Bot is starting...")

    bot.infinity_polling(
        skip_pending=True
    )
