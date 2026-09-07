import os
import json
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


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass

    return {"users": {}}


data = load_data()
users = data.get("users", {})


def save_data():
    data["users"] = users

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


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


# ==================================================
# BOT MENU
# ==================================================

def set_commands():

    commands = [
        telebot.types.BotCommand("start", "Start Bot"),
        telebot.types.BotCommand("balance", "Check Balance"),
        telebot.types.BotCommand("game", "Game Menu"),
        telebot.types.BotCommand("usd", "Add USD"),
        telebot.types.BotCommand("dia", "Add Diamonds"),
        telebot.types.BotCommand("giftusd", "Gift USD")
    ]

    bot.set_my_commands(commands)


# ==================================================
# START
# ==================================================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Player"

    user = get_user(user_id)

    text = (
        f'👋 မင်္ဂလာပါ '
        f'<a href="tg://user?id={user_id}">{user_name}</a>!\n\n'
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

    user = get_user(user_id)

    text = (
        f"👤 <b>{user_name} ({user_id})</b> ၏ လက်ကျန်ငွေ\n"
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

    text = (
        f'👋 <a href="tg://user?id={user_id}">{user_name}</a> ရေ!\n\n'
        '🎮 ဆော့ကစားနိုင်သောဂိမ်းများ'
    )

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "🎰 Slot",
            callback_data="game_slot"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# SLOT BUTTON
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data == "game_slot")
def slot_button(call):

    bot.answer_callback_query(
        call.id,
        "🎰 Slot Game ကို မကြာခင်ထည့်ပေးမယ်!"
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

    user = get_user(message.from_user.id)

    user["usd"] += amount
    save_data()

    bot.reply_to(
        message,
        f"✅ USD ထည့်ပြီးပါပြီ!\n\n"
        f"💵 +${amount:,}\n"
        f"💰 လက်ကျန်: ${user['usd']:,}USD"
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

    user = get_user(message.from_user.id)

    user["dia"] += amount
    save_data()

    bot.reply_to(
        message,
        f"✅ Diamond ထည့်ပြီးပါပြီ!\n\n"
        f"💎 +{amount:,}\n"
        f"💎 လက်ကျန်: {user['dia']:,} Diamonds"
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

    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            "✅ Confirm",
            callback_data=f"confirm_usd:{target.id}:{amount}"
        ),
        InlineKeyboardButton(
            "❌ Cancel",
            callback_data="cancel_gift"
        )
    )

    bot.reply_to(
        message,
        f"🎁 <b>USD Gift အတည်ပြုရန်</b>\n\n"
        f"👤 {target.first_name}\n"
        f"💵 ပေးမည့်ပမာဏ: <b>${amount:,} USD</b>\n\n"
        f"အောက်က ခလုတ်ကိုနှိပ်ပြီး အတည်ပြုပါ။",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# CONFIRM USD
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("confirm_usd:")
)
def confirm_usd(call):

    if not call.from_user.username:
        bot.answer_callback_query(
            call.id,
            "❌ Owner သာ Confirm လုပ်နိုင်ပါတယ်။",
            show_alert=True
        )
        return

    if call.from_user.username.lower() != OWNER_USERNAME.lower():
        bot.answer_callback_query(
            call.id,
            "❌ Owner သာ Confirm လုပ်နိုင်ပါတယ်။",
            show_alert=True
        )
        return

    try:
        _, target_id, amount = call.data.split(":")
        target_id = int(target_id)
        amount = int(amount)
    except:
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
        f"🎁 <b>USD Gift ပေးပြီးပါပြီ!</b>\n\n"
        f"👤 {call.message.reply_to_message.from_user.first_name if call.message.reply_to_message else 'User'}\n"
        f"💵 +${amount:,} USD",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )


# ==================================================
# CANCEL GIFT
# ==================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "cancel_gift"
)
def cancel_gift(call):

    if not call.from_user.username:
        bot.answer_callback_query(
            call.id,
            "❌ Owner သာ Cancel လုပ်နိုင်ပါတယ်။",
            show_alert=True
        )
        return

    if call.from_user.username.lower() != OWNER_USERNAME.lower():
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
# RENDER
# ==================================================

@app.route("/")
def home():
    return "Game Bot is running!"


def run():

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )


Thread(target=run).start()


# ==================================================
# START BOT
# ==================================================

print("Bot is starting...")

set_commands()

bot.infinity_polling()
