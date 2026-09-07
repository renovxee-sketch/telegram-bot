import os
import random
import telebot
from flask import Flask
from threading import Thread
from pymongo import MongoClient

TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
MONGO_URL = os.environ.get("MONGO_URL", "your_mongo_url")

# yaung ရဲ့ Telegram User ID ကို ဒီနေရာမှာ ထည့်ပါ (ဥပမာ: 123456789)
OWNER_ID = 8032394583  # <--- ဒီ 0 နေရာမှာ yaung ရဲ့ ID အမှန်ကို ထည့်ပေးပါ

bot = telebot.TeleBot(TOKEN)

mongo_client = MongoClient(MONGO_URL)
db = mongo_client["telegram_game_bot"]
users_col = db["users"]

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

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
            "လက်ကျန်ငွေ စစ်ဆေးရန် `/balance` ကိုသုံးပါ။"
        )

    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown")

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

# Owner Only: /usd (User မက်ဆေ့ချ်ကို Reply လုပ်ပြီး /usd <amount> ဟု ပို့ပါ)
@bot.message_handler(commands=["usd"])
def add_usd(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ ဒီ command က Owner yaung သာ သုံးလို့ရပါတယ်။")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ ငွေဖြည့်ပေးလိုသော User ၏ မက်ဆေ့ချ်ကို **Reply** လုပ်ပြီးမှ `/usd <amount>` ဟု ပို့ပါ။", parse_mode="Markdown")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ ပုံစံ - `/usd <ပမာဏ>` (ဥပမာ: `/usd 5000`)", parse_mode="Markdown")
        return

    try:
        amount = float(args[1])
    except ValueError:
        bot.reply_to(message, "❌ ထည့်သွင်းမည့် ပမာဏ မမှန်ကန်ပါ။ ဂဏန်းသာ ရေးပါ။")
        return

    target_user_id = message.reply_to_message.from_user.id
    user = users_col.find_one({"user_id": target_user_id})
    
    if user:
        new_usd = user.get("usd", 0) + amount
        users_col.update_one({"user_id": target_user_id}, {"$set": {"usd": new_usd}})
    else:
        new_usd = amount
        users_col.insert_one({"user_id": target_user_id, "usd": new_usd, "dia": 500})

    bot.reply_to(message, f"✅ အောင်မြင်ပါသည်။ User ထံသို့ **{amount:,.2f} USD** ထည့်သွင်းပေးလိုက်ပါပြီ။", parse_mode="Markdown")

# Owner Only: /dia (User မက်ဆေ့ချ်ကို Reply လုပ်ပြီး /dia <amount> ဟု ပို့ပါ)
@bot.message_handler(commands=["dia"])
def add_dia(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ ဒီ command က Owner yaung သာ သုံးလို့ရပါတယ်။")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ Dia ဖြည့်ပေးလိုသော User ၏ မက်ဆေ့ချ်ကို **Reply** လုပ်ပြီးမှ `/dia <amount>` ဟု ပို့ပါ။", parse_mode="Markdown")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ ပုံစံ - `/dia <ပမာဏ>` (ဥပမာ: `/dia 100`)", parse_mode="Markdown")
        return

    try:
        amount = int(args[1])
    except ValueError:
        bot.reply_to(message, "❌ ထည့်သွင်းမည့် ပမာဏ မမှန်ကန်ပါ။ ဂဏန်းသာ ရေးပါ။")
        return

    target_user_id = message.reply_to_message.from_user.id
    user = users_col.find_one({"user_id": target_user_id})
    
    if user:
        new_dia = user.get("dia", 0) + amount
        users_col.update_one({"user_id": target_user_id}, {"$set": {"dia": new_dia}})
    else:
        new_dia = amount
        users_col.insert_one({"user_id": target_user_id, "usd": 10000.0, "dia": new_dia})

    bot.reply_to(message, f"✅ အောင်မြင်ပါသည်။ User ထံသို့ **{amount} Dia** ထည့်သွင်းပေးလိုက်ပါပြီ။", parse_mode="Markdown")

@bot.message_handler(commands=["game"])
def game_menu(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    bets = [10, 100, 1000, 10000, 100000, 1000000]
    buttons = []
    for b in bets:
        label = f"{b:,}" if b < 1000000 else f"{b // 1000000}M"
        if b == 1000: label = "1k"
        buttons.append(telebot.types.InlineKeyboardButton(f"🎰 {label} USD", callback_data=f"play_{b}"))
    markup.add(*buttons)
    bot.send_message(
        message.chat.id, 
        "🎰 **Slot Game သို့ ကြိုဆိုပါတယ် yaung!**\n\nအောက်ပါ လောင်းကြေးတစ်ခုကို ရွေးချယ်ပါ -", 
        parse_mode="Markdown", 
        reply_markup=markup
    )

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
        msg = f"🎰 **SLOT GAME RESULT** 🎰\n\nရလဒ်: {result_str}\n\n🎉 ဂုဏ်ယူပါတယ် yaung! **{multiplier}x** ဖြင့် **{win_amount:,} USD** နိုင်သွားပါပြီ!\n💰 လက်ကျန်ငွေ: `{new_usd:,.2f} USD`"
    else:
        new_usd = current_usd - bet_amount
        users_col.update_one({"user_id": user_id}, {"$set": {"usd": new_usd}})
        msg = f"🎰 **SLOT GAME RESULT** 🎰\n\nရလဒ်: {result_str}\n\n😢 စိတ်မကောင်းပါဘူး yaung, ရှုံးသွားပါတယ်။\n💸 လောင်းကြေး `- {bet_amount:,} USD`\n💰 လက်ကျန်ငွေ: `{new_usd:,.2f} USD`"
        
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, parse_mode="Markdown")

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    try:
        bot.remove_webhook()
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Error: {e}")
