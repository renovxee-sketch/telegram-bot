import os
import random
import telebot
from flask import Flask
from threading import Thread
from pymongo import MongoClient

# 1. Environment Variables များနှင့် ချိတ်ဆက်ခြင်း
TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
MONGO_URL = os.environ.get("MONGO_URL", "your_mongo_url")
# Owner ရဲ့ Telegram User ID ကို ထည့်ရန် (Render env မှာ OWNER_ID ထည့်ရပါမယ်)
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

bot = telebot.TeleBot(TOKEN)

# MongoDB ချိတ်ဆက်ခြင်း
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["telegram_game_bot"]
users_col = db["users"]

# Render တွင် Port error မတက်စေရန် Flask ဆာဗာ
app = Flask('')

@app.route('/')
def home():
    return "Game Bot with Economy is running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# 2. /start Command (USD 10,000 နဲ့ Dia 500 စတင်ထည့်ပေးခြင်း)
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    user = users_col.find_one({"user_id": user_id})
    if not user:
        users_col.insert_one({
            "user_id": user_id,
            "username": message.from_user.username,
            "usd": 10000.0,
            "dia": 500
        })
        welcome_msg = (
            f"မင်္ဂလာပါ *{user_name}* (yaung) ရေ! 👋\n\n"
            "Bot က အောင်မြင်စွာ အလုပ်လုပ်နေပါပြီ။ 🚀\n"
            "🎁 ကြိုဆိုလက်ဆောင်အနေဖြင့် **USD 10,000** နှင့် **Dia 500** ထည့်သွင်းပေးလိုက်ပါပြီ!\n\n"
            "ဂိမ်းစဆော့ရန် `/game` ကိုနှိပ်ပါ သို့မဟုတ် လက်ကျန်ငွေကြည့်ရန် `/balance` ကိုသုံးပါ။"
        )
    else:
        welcome_msg = (
            f"မင်္ဂလာပါ *{user_name}* (yaung) ရေ ပြန်လည်ကြိုဆိုပါတယ်! 👋\n"
            "လက်ကျန်ငွေ စစ်ဆေးရန် `/balance` ကိုနှိပ်ပါ သို့မဟုတ် ဂိမ်းဆော့ရန် `/game` ကိုသုံးပါ။"
        )

    bot_user_name = bot.get_me().username
    markup = telebot.types.InlineKeyboardMarkup()
    group_button = telebot.types.InlineKeyboardButton(
        "➕ Add Me To Your Group", 
        url=f"https://t.me/{bot_user_name}?startgroup=true"
    )
    markup.add(group_button)
    
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup)

# 3. /balance Command (ငွေစာရင်းကြည့်ရန်)
@bot.message_handler(commands=["balance"])
def balance(message):
    user_id = message.from_user.id
    user = users_col.find_one({"user_id": user_id})
    
    if user:
        usd = user.get("usd", 0)
        dia = user.get("dia", 0)
    else:
        usd = 10000.0
        dia = 500
        users_col.insert_one({"user_id": user_id, "usd": usd, "dia": dia})
        
    bal_text = (
        "💰 **သင့်ရဲ့ လက်ကျန်ငွေစာရင်း:**\n\n"
        f"💵 USD: `{usd:,.2f}`\n"
        f"💎 Dia: `{dia}`"
    )
    bot.send_message(message.chat.id, bal_text, parse_mode="Markdown")

# 4. Owner Only: /usd Command (USD ဖြည့်ရန်)
@bot.message_handler(commands=["usd"])
def add_usd(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ ဒီ command က Owner သာ သုံးလို့ရပါတယ်။")
        return

    args = message.text.split()
    target_user_id = None
    amount = None

    # Reply လုပ်ထားလျှင်
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        if len(args) > 1:
            try:
                amount = float(args[1])
            except ValueError:
                pass
    # ID နှင့် ပမာဏ တိုက်ရိုက်ပေးလျှင် (/usd user_id amount)
    elif len(args) >= 3:
        try:
            target_user_id = int(args[1])
            amount = float(args[2])
        except ValueError:
            pass

    if not target_user_id or amount is None:
        bot.reply_to(message, "⚠️ အသုံးစနစ်မှားယွင်းနေပါသည်။\nပုံစံ - `/usd <user_id> <amount>` (သို့မဟုတ်) User မက်ဆေ့ချ်ကို Reply လုပ်ပြီး `/usd <amount>` လို့ ပို့ပါ။", parse_mode="Markdown")
        return

    user = users_col.find_one({"user_id": target_user_id})
    if user:
        new_usd = user.get("usd", 0) + amount
        users_col.update_one({"user_id": target_user_id}, {"$set": {"usd": new_usd}})
    else:
        new_usd = amount
        users_col.insert_one({"user_id": target_user_id, "usd": new_usd, "dia": 500})

    bot.reply_to(message, f"✅ အောင်မြင်ပါသည်။ User (`{target_user_id}`) ထံသို့ **{amount:,.2f} USD** ထည့်သွင်းပေးလိုက်ပါပြီ။\nလက်ကျန် USD: `{new_usd:,.2f}`", parse_mode="Markdown")

# 5. Owner Only: /dia Command (Diamonds ဖြည့်ရန်)
@bot.message_handler(commands=["dia"])
def add_dia(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ ဒီ command က Owner သာ သုံးလို့ရပါတယ်။")
        return

    args = message.text.split()
    target_user_id = None
    amount = None

    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        if len(args) > 1:
            try:
                amount = int(args[1])
            except ValueError:
                pass
    elif len(args) >= 3:
        try:
            target_user_id = int(args[1])
            amount = int(args[2])
        except ValueError:
            pass

    if not target_user_id or amount is None:
        bot.reply_to(message, "⚠️ အသုံးစနစ်မှားယွင်းနေပါသည်။\nပုံစံ - `/dia <user_id> <amount>` (သို့မဟုတ်) User မက်ဆေ့ချ်ကို Reply လုပ်ပြီး `/dia <amount>` လို့ ပို့ပါ။", parse_mode="Markdown")
        return

    user = users_col.find_one({"user_id": target_user_id})
    if user:
        new_dia = user.get("dia", 0) + amount
        users_col.update_one({"user_id": target_user_id}, {"$set": {"dia": new_dia}})
    else:
        new_dia = amount
        users_col.insert_one({"user_id": target_user_id, "usd": 10000.0, "dia": new_dia})

    bot.reply_to(message, f"✅ အောင်မြင်ပါသည်။ User (`{target_user_id}`) ထံသို့ **{amount} Dia** ထည့်သွင်းပေးလိုက်ပါပြီ။\nလက်ကျန် Dia: `{new_dia}`", parse_mode="Markdown")

# 6. /game Command (လောင်းကြေးခလုတ်များပြသရန်)
@bot.message_handler(commands=["game"])
def game_menu(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    bets = [10, 100, 1000, 10000, 100000, 300000, 500000, 1000000]
    
    buttons = []
    for b in bets:
        if b < 1000000:
            label = f"{b:,}"
            if b == 1000: label = "1k"
        else:
            label = f"{b // 1000000}M"
        buttons.append(telebot.types.InlineKeyboardButton(f"🎰 {label} USD", callback_data=f"play_{b}"))
        
    markup.add(*buttons)
    bot.send_message(
        message.chat.id, 
        "🎰 **Slot Game သို့ ကြိုဆိုပါတယ် yaung!**\n\nအောက်ပါ လောင်းကြေးတစ်ခုကို ရွေးချယ်ပါ -", 
        parse_mode="Markdown", 
        reply_markup=markup
    )

# 7. Callback Query (Slot ဂိမ်းကစားခြင်း)
@bot.callback_query_handler(func=lambda call: call.data.startswith("play_"))
def play_slot(call):
    user_id = call.from_user.id
    bet_amount = int(call.data.split("_")[1])
    
    user = users_col.find_one({"user_id": user_id})
    current_usd = user.get("usd", 0) if user else 10000.0
    
    if current_usd < bet_amount:
        bot.answer_callback_query(call.id, "❌ သင့်မှာ USD လက်ကျန် မလုံလောက်ပါ!", show_alert=True)
        return
    
    symbols = ["🍇", "7", "BAR", "🍋", "🔔"]
    spin1 = random.choice(symbols)
    spin2 = random.choice(symbols)
    spin3 = random.choice(symbols)
    
    result_str = f"{spin1} | {spin2} | {spin3}"
    
    multiplier = 0
    if spin1 == "7" and spin2 == "7" and spin3 == "7":
        multiplier = 30
    elif spin1 == "BAR" and spin2 == "BAR" and spin3 == "BAR":
        multiplier = 10
    elif spin1 == spin2 == spin3:
        multiplier = 5
        
    if multiplier > 0:
        win_amount = bet_amount * multiplier
        new_usd = current_usd + win_amount
        users_col.update_one({"user_id": user_id}, {"$set": {"usd": new_usd}})
        msg = (
            f"🎰 **SLOT GAME RESULT** 🎰\n\n"
            f"ရလဒ်: {result_str}\n\n"
            f"🎉 ဂုဏ်ယူပါတယ် yaung! **{multiplier}x** ဖြင့် **{win_amount:,} USD** နိုင်သွားပါပြီ!\n"
            f"💰 လက်ကျန်ငွေ: `{new_usd:,.2f} USD`"
        )
    else:
        new_usd = current_usd - bet_amount
        users_col.update_one({"user_id": user_id}, {"$set": {"usd": new_usd}})
        msg = (
            f"🎰 **SLOT GAME RESULT** 🎰\n\n"
            f"ရလဒ်: {result_str}\n\n"
            f"😢 စိတ်မကောင်းပါဘူး yaung, ရှုံးသွားပါတယ်။\n"
            f"💸 လောင်းကြေး `- {bet_amount:,} USD`\n"
            f"💰 လက်ကျန်ငွေ: `{new_usd:,.2f} USD`"
        )
        
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=msg,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["dice"])
def dice(message):
    bot.send_dice(message.chat.id, emoji='🎲')

@bot.message_handler(commands=["bowling"])
def bowling(message):
    bot.send_dice(message.chat.id, emoji='🎳')

@bot.message_handler(commands=["football"])
def football(message):
    bot.send_dice(message.chat.id, emoji='⚽')

@bot.message_handler(commands=["basketball"])
def basketball(message):
    bot.send_dice(message.chat.id, emoji='🏀')

@bot.message_handler(commands=["slot"])
def slot_command(message):
    game_menu(message)

@bot.message_handler(commands=["dart"])
def dart(message):
    bot.send_dice(message.chat.id, emoji='🎯')

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    bot.infinity_polling()
