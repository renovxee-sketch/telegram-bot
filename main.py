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

app = Flask(__name__)


# =========================================================
# FLASK
# =========================================================

@app.route("/")
def home():
    return "Bot is running!"


def run_flask():
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================================================
# DATA
# =========================================================

def load_data():

    if not os.path.exists(DATA_FILE):
        return {}

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


data = load_data()


def save_data():

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def get_user(
    user_id,
    first_name="User",
    username=None
):

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

    return (
        f'<a href="tg://user?id={user.id}">'
        f'{name}'
        f'</a>'
    )


def money(value):

    return f"{value:,}"


def is_owner(message):

    username = message.from_user.username

    if not username:
        return False

    return (
        username.lower()
        == OWNER_USERNAME.lower()
    )


def balance_text(
    user,
    user_id
):

    return (
        f"👤 {user['name']} ({user_id}) "
        "၏ လက်ကျန်ငွေ\n\n"

        f"💎 Diamonds: "
        f"{money(user['dia'])}💎\n"

        f"💵 USD: "
        f"${money(user['usd'])}USD"
    )


# =========================================================
# START
# =========================================================

@bot.message_handler(
    commands=["start"]
)
def start_command(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )

    text = (
        f"👋 မင်္ဂလာပါ "
        f"{mention_user(message.from_user)}!\n\n"

        "🎮 အပျော်တန်း Game ကစားတဲ့ "
        "Bot မှ ကြိုဆိုပါတယ်!\n\n"

        f"💎 Diamonds: "
        f"{money(user['dia'])}💎\n"

        f"💵 USD: "
        f"${money(user['usd'])}USD\n\n"

        "👇 အောက်ပါ Button ကို နှိပ်ပြီး "
        "သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!"
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

@bot.message_handler(
    commands=["balance"]
)
def balance_command(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )

    bot.reply_to(
        message,
        balance_text(
            user,
            message.from_user.id
        )
    )


# =========================================================
# GAME
# =========================================================

@bot.message_handler(
    commands=["game"]
)
def game_command(message):

    user = get_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )

    game_owner_id = message.from_user.id

    text = (
        "╔════════════════════════════╗\n"
        "        🎰 CASINO 🎰\n"
        "╚════════════════════════════╝\n\n"

        f"👤 {mention_user(message.from_user)}\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "💰 YOUR BALANCE\n\n"

        f"💵 USD   ┃  ${money(user['usd'])}\n"
        f"💎 DIA   ┃  {money(user['dia'])}💎\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "🎮 GAME CENTER\n\n"

        "🎰 SLOT MACHINE\n\n"

        "🍀 သင့်ကံကို စမ်းသပ်ပါ!\n"
        "💰 လောင်းကြေးရွေးပြီး စတင်ကစားပါ\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "⚠️ ဒီ Game ကို ဖော်ထားတဲ့သူက\n"
        "သူကိုယ်တိုင်ပဲ ကစားနိုင်ပါတယ်။\n\n"

        "👇 PLAY NOW 👇"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🎰  PLAY SLOT MACHINE  🎰",
            callback_data=f"game_slot:{game_owner_id}"
        )
    )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# =========================================================
# GAME OWNER CHECK
# =========================================================

def check_game_owner(
    call,
    owner_id
):

    if call.from_user.id != owner_id:

        bot.answer_callback_query(
            call.id,
            "🚫 ဒီ Game က မင်းဖော်ထားတာမဟုတ်ပါ!\n\n"
            "🎰 ကိုယ်တိုင် /game ဖော်ပြီးမှ\n"
            "ကိုယ်တိုင်ကစားနိုင်ပါတယ်။",
            show_alert=True
        )

        return False

    return True


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


def create_bet_keyboard(
    owner_id
):

    markup = types.InlineKeyboardMarkup()

    for amount in BET_AMOUNTS:

        markup.add(
            types.InlineKeyboardButton(
                f"💵  {bet_name(amount)}  💵",
                callback_data=(
                    f"slot_bet:{owner_id}:{amount}"
                )
            )
        )

    return markup


# =========================================================
# SLOT MACHINE SCREEN
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("game_slot:")
)
def slot_button(call):

    try:

        owner_id = int(
            call.data.split(":")[1]
        )

    except Exception:

        bot.answer_callback_query(
            call.id,
            "❌ Game Error",
            show_alert=True
        )

        return


    if not check_game_owner(
        call,
        owner_id
    ):

        return


    user = get_user(
        call.from_user.id,
        call.from_user.first_name,
        call.from_user.username
    )

    bot.answer_callback_query(
        call.id
    )


    text = (
        "╔════════════════════════════╗\n"
        "        🎰 SLOT MACHINE 🎰\n"
        "╚════════════════════════════╝\n\n"

        f"👤 {mention_user(call.from_user)}\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "💰 YOUR BALANCE\n\n"

        f"💵 USD  ┃  ${money(user['usd'])}\n"
        f"💎 DIA  ┃  {money(user['dia'])}💎\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "🎰  🍋   🍇   7️⃣   BAR  🎰\n\n"

        "🍀 ကံကောင်းရင် ဆုကြီးတွေ ရနိုင်ပါတယ်!\n\n"

        "🏆 777       → 30×\n"
        "🏆 BAR BAR BAR → 10×\n"
        "🏆 77🍇      → 3×\n"
        "🏆 🍇77      → 3×\n"
        "🏆 77 BAR    → 3×\n"
        "🏆 3 Fruits  → 5×\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "💵 လောင်းကြေးရွေးပါ 👇"
    )


    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=create_bet_keyboard(
            owner_id
        ),
        parse_mode="HTML"
    )


# =========================================================
# SLOT DECODER
# =========================================================

def get_slot_combination(
    dice_value
):

    symbols = [
        "BAR",
        "🍇",
        "🍋",
        "7️⃣"
    ]

    value = dice_value - 1

    left = value & 3

    middle = (
        value >> 2
    ) & 3

    right = (
        value >> 4
    ) & 3

    return (
        symbols[left],
        symbols[middle],
        symbols[right]
    )


# =========================================================
# SLOT PAYOUT
# =========================================================

def get_slot_payout(
    dice_value
):

    left, middle, right = (
        get_slot_combination(
            dice_value
        )
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


    # 7🍇7 = LOSS

    if (
        left == "7️⃣"
        and middle == "🍇"
        and right == "7️⃣"
    ):

        return 0


    # Three identical fruits = 5x

    if left == middle == right:

        if left in [
            "🍇",
            "🍋"
        ]:

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

    left, middle, right = (
        get_slot_combination(
            dice_value
        )
    )

    combination = (
        f"{left}   {middle}   {right}"
    )


    current_user = get_user(
        telegram_user.id,
        telegram_user.first_name,
        telegram_user.username
    )


    if multiplier > 0:

        winnings = (
            bet * multiplier
        )

        result_text = (

            "╔════════════════════════════╗\n"
            "          🎰 RESULT 🎰\n"
            "╚════════════════════════════╝\n\n"

            f"👤 {mention_user(telegram_user)}\n\n"

            f"🎰  {combination}\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "🎉🎉 အနိုင်ရပါတယ်! 🎉🎉\n\n"

            f"🏆 ဆုကြေး ┃ {multiplier}×\n"

            f"💰 အနိုင်ရငွေ ┃ "
            f"${money(winnings)} USD\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "💰 CURRENT BALANCE\n\n"

            f"💵 USD ┃ "
            f"${money(current_user['usd'])}\n"

            f"💎 DIA ┃ "
            f"{money(current_user['dia'])}💎\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "🍀 နောက်တစ်ကြိမ်လည်း "
            "ကံကောင်းပါစေ!\n\n"

            "👇 နောက်တစ်ကြိမ် လောင်းကြေးရွေးပါ 👇"
        )

    else:

        result_text = (

            "╔════════════════════════════╗\n"
            "          🎰 RESULT 🎰\n"
            "╚════════════════════════════╝\n\n"

            f"👤 {mention_user(telegram_user)}\n\n"

            f"🎰  {combination}\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "😢 ဒီတစ်ခါ ရှုံးသွားပါတယ်။\n\n"

            f"💸 ရှုံးကြေး ┃ "
            f"${money(bet)} USD\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "💰 CURRENT BALANCE\n\n"

            f"💵 USD ┃ "
            f"${money(current_user['usd'])}\n"

            f"💎 DIA ┃ "
            f"{money(current_user['dia'])}💎\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "🍀 နောက်တစ်ကြိမ် ကံကောင်းပါစေ!\n\n"

            "👇 နောက်တစ်ကြိမ် လောင်းကြေးရွေးပါ 👇"
        )


    bot.reply_to(
        dice_message,
        result_text,
        reply_markup=create_bet_keyboard(
            owner_id
        ),
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
            "❌ လောင်းကြေးမမှန်ပါ။"
        )

        return


    # ONLY GAME OWNER

    if not check_game_owner(
        call,
        owner_id
    ):

        return


    # VALID BET CHECK

    if bet not in BET_AMOUNTS:

        bot.answer_callback_query(
            call.id,
            "❌ ဒီလောင်းကြေး မရှိပါ။"
        )

        return


    user = get_user(
        call.from_user.id,
        call.from_user.first_name,
        call.from_user.username
    )


    # BALANCE CHECK

    if user["usd"] < bet:

        bot.answer_callback_query(
            call.id,
            "❌ Balance မလုံလောက်ပါ!",
            show_alert=True
        )

        return


    # DEDUCT BET

    user["usd"] -= bet

    save_data()


    bot.answer_callback_query(
        call.id,
        "🎰 Good Luck! 🍀"
    )


    # TELEGRAM REAL SLOT

    dice_msg = bot.send_dice(
        call.message.chat.id,
        emoji="🎰"
    )


    # WAIT FOR ANIMATION

    time.sleep(4)


    # GET RESULT

    dice_value = (
        dice_msg.dice.value
    )

    multiplier = get_slot_payout(
        dice_value
    )


    # ADD WINNINGS

    if multiplier > 0:

        winnings = (
            bet * multiplier
        )

        user["usd"] += winnings

        save_data()


    # SEND RESULT

    send_slot_result(
        dice_msg,
        call.from_user,
        bet,
        multiplier,
        dice_value,
        owner_id
    )


# =========================================================
# OWNER USD
# =========================================================

@bot.message_handler(
    commands=["usd"]
)
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

        amount = int(
            parts[1]
        )

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

        f"✅ USD ${money(amount)} "
        "ထည့်ပြီးပါပြီ။\n\n"

        f"💵 Balance ┃ "
        f"${money(user['usd'])}"
    )


# =========================================================
# OWNER DIA
# =========================================================

@bot.message_handler(
    commands=["dia"]
)
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

        amount = int(
            parts[1]
        )

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

        f"✅ Diamonds "
        f"{money(amount)}💎 "
        "ထည့်ပြီးပါပြီ။\n\n"

        f"💎 Balance ┃ "
        f"{money(user['dia'])}💎"
    )


# =========================================================
# GIFT CONFIRM SYSTEM
# =========================================================

def create_gift_confirm_keyboard(
    gift_type,
    target_id,
    amount,
    sender_id
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
                f"{sender_id}"
            )
        ),

        types.InlineKeyboardButton(
            "❌ CANCEL",
            callback_data=(
                f"gift_cancel:"
                f"{sender_id}"
            )
        )
    )


    return markup


# =========================================================
# GIFT
# =========================================================

@bot.message_handler(
    commands=["gift"]
)
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

            "❌ User ရဲ့ message ကို "
            "Reply လုပ်ပြီး\n\n"

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

        amount = int(
            parts[1]
        )

    except ValueError:

        bot.reply_to(
            message,
            "❌ Amount မမှန်ပါ။"
        )

        return


    if amount <= 0:

        bot.reply_to(
            message,
            "❌ Amount မှန်ကန်စွာ ထည့်ပါ။"
        )

        return


    target = (
        message.reply_to_message.from_user
    )


    text = (

        "╔════════════════════════════╗\n"
        "        🎁 USD GIFT 🎁\n"
        "╚════════════════════════════╝\n\n"

        f"👤 User ┃ "
        f"{mention_user(target)}\n\n"

        f"💵 Amount ┃ "
        f"${money(amount)} USD\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "⚠️ ဒီ Gift ကို ပေးမှာ သေချာပါသလား?\n\n"

        "👇 Confirm လုပ်ရန် သို့မဟုတ် Cancel လုပ်ပါ"
    )


    bot.reply_to(
        message,
        text,
        reply_markup=create_gift_confirm_keyboard(
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

@bot.message_handler(
    commands=["giftdia"]
)
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

            "❌ User ရဲ့ message ကို "
            "Reply လုပ်ပြီး\n\n"

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

        amount = int(
            parts[1]
        )

    except ValueError:

        bot.reply_to(
            message,
            "❌ Amount မမှန်ပါ။"
        )

        return


    if amount <= 0:

        bot.reply_to(
            message,
            "❌ Amount မှန်ကန်စွာ ထည့်ပါ။"
        )

        return


    target = (
        message.reply_to_message.from_user
    )


    text = (

        "╔════════════════════════════╗\n"
        "       🎁 DIA GIFT 🎁\n"
        "╚════════════════════════════╝\n\n"

        f"👤 User ┃ "
        f"{mention_user(target)}\n\n"

        f"💎 Amount ┃ "
        f"{money(amount)} DIA\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "⚠️ ဒီ Diamond Gift ကို "
        "ပေးမှာ သေချာပါသလား?\n\n"

        "👇 Confirm လုပ်ရန် သို့မဟုတ် Cancel လုပ်ပါ"
    )


    bot.reply_to(
        message,
        text,
        reply_markup=create_gift_confirm_keyboard(
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

        sender_id = int(parts[4])

    except Exception:

        bot.answer_callback_query(
            call.id,
            "❌ Error"
        )

        return


    # ONLY THE PERSON WHO CREATED GIFT

    if call.from_user.id != sender_id:

        bot.answer_callback_query(
            call.id,

            "🚫 ဒီ Confirm ခလုတ်ကို "
            "Gift ပေးတဲ့သူပဲ နှိပ်နိုင်ပါတယ်။",

            show_alert=True
        )

        return


    target = get_user(
        target_id
    )


    # USD

    if gift_type == "usd":

        target["usd"] += amount

        save_data()


        bot.answer_callback_query(
            call.id,
            "✅ Gift Confirmed!"
        )


        bot.edit_message_text(

            "╔════════════════════════════╗\n"
            "       🎁 GIFT SUCCESS 🎁\n"
            "╚════════════════════════════╝\n\n"

            f"👤 User ┃ "
            f"{target['name']}\n\n"

            f"💵 +${money(amount)} USD\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "✅ Gift ပေးပြီးပါပြီ!\n\n"

            f"💰 Balance ┃ "
            f"${money(target['usd'])} USD",

            call.message.chat.id,
            call.message.message_id
        )


    # DIA

    elif gift_type == "dia":

        target["dia"] += amount

        save_data()


        bot.answer_callback_query(
            call.id,
            "✅ Gift Confirmed!"
        )


        bot.edit_message_text(

            "╔════════════════════════════╗\n"
            "       🎁 GIFT SUCCESS 🎁\n"
            "╚════════════════════════════╝\n\n"

            f"👤 User ┃ "
            f"{target['name']}\n\n"

            f"💎 +{money(amount)} DIA\n\n"

            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "✅ Diamond Gift ပေးပြီးပါပြီ!\n\n"

            f"💎 Balance ┃ "
            f"{money(target['dia'])} DIA",

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

    try:

        sender_id = int(
            call.data.split(":")[1]
        )

    except Exception:

        bot.answer_callback_query(
            call.id,
            "❌ Error"
        )

        return


    # ONLY CREATOR

    if call.from_user.id != sender_id:

        bot.answer_callback_query(
            call.id,

            "🚫 ဒီ Cancel ခလုတ်ကို "
            "Gift ပေးတဲ့သူပဲ နှိပ်နိုင်ပါတယ်။",

            show_alert=True
        )

        return


    bot.answer_callback_query(
        call.id,
        "❌ Cancelled"
    )


    bot.edit_message_text(

        "╔════════════════════════════╗\n"
        "          ❌ CANCELLED\n"
        "╚════════════════════════════╝\n\n"

        "🎁 Gift လုပ်ဆောင်ချက်ကို\n"
        "ပယ်ဖျက်လိုက်ပါပြီ။",

        call.message.chat.id,
        call.message.message_id
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


    bot.set_my_commands(
        commands
    )


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


    print(
        "Bot is running..."
    )


    bot.remove_webhook()


    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
