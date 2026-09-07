import os
import random
import time
import telebot
from flask import Flask
from threading import Thread
from pymongo import MongoClient

TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
MONGO_URL = os.environ.get("MONGO_URL", "your_mongo_url")

# yaung ရဲ့ Telegram User ID ကို ဒီမှာ ထည့်ပါ
OWNER_ID = 8032394583  # <--- ဒီ 0 နေရာမှာ yaung ရဲ့ ID အမှန်ကို ထည့်ပါ

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
        usd_val = 10000.0
        dia_val = 500
    else:
        usd_val = user.get("usd", 0)
        dia_val = user.get("dia", 0)

    welcome_msg = (
        f"လက်စတန်း Game ကစားတဲ့ Bot မှ ကြိုဆိုပါတယ်! 👋\n"
        f"💎 Diamonds: `{dia_val:,}` 💎\n"
        f"💵 USD Balance: `${usd_val:,.0f} USD`\n\n"
        "👇 အောက်ပါ Button ကို နှိပ်ပြီး သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!"
    )

    bot_user_name = bot.get_me().username
    markup = telebot.types.InlineKeyboardMarkup()
    group_button = telebot.types.InlineKeyboardButton(
        "➕ Add Me Your GP", 
        url=f"https://t.me/{bot_user_name}?startgroup=true"
    )
    markup.add(group_button)
    
    bot.send_message(message.chat.id, f"👋 မင်္ဂလာပါ {user_name}!\n\n{welcome_msg}", parse_mode="Markdown", reply_markup=markup)

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
        f"💎 Diamonds: `{dia:,}` 💎\n"
        f"💵 USD Balance: `${usd:,.0f} USD`"
    )
    bot.send_message(message.chat.id, bal_text, parse_mode="Markdown")

# Owner Only: /usd
@bot.message_handler(commands=["usd"])
def add_usd(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ ဒီ command က Owner yaung သာ သုံးလို့ရပါတယ်။")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ ငွေဖြည့်လိုသော User ၏ မက်ဆေ့ချ်ကို Reply လုပ်ပြီး `/usd <amount>` ဟု ပို့ပါ။")
        return
    args = message.text.split()
    try:
        amount = float(args[1])
    except:
        return bot.reply_to(message, "❌ ပမာဏ မမှန်ကန်ပါ။")

    target_user_id = message.reply_to_message.from_user.id
    user = users_col.find_one({"user_id": target_user_id})
    if user:
        new_usd = user.get("usd", 0) + amount
        users_col.update_one({"user_id": target_user_id}, {"$set": {"usd": new_usd}})
    else:
        users_col.insert_one({"user_id": target_user_id, "usd": amount, "dia": 500})
    bot.reply_to(message, f"✅ User ထံသို့ **{amount:,.0f} USD** ထည့်သွင်းပြီးပါပြီ။", parse_mode="Markdown")

# Owner Only: /dia
@bot.message_handler(commands=["dia"])
def add_dia(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ ဒီ command က Owner yaung သာ သုံးလို့ရပါတယ်။")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Dia ဖြည့်လိုသော User ၏ မက်ဆေ့ချ်ကို Reply လုပ်ပြီး `/dia <amount>` ဟု ပို့ပါ။")
        return
    args = message.text.split()
    try:
        amount = int(args[1])
    except:
        return bot.reply_to(message, "❌ ပမာဏ မမှန်ကန်ပါ။")

    target_user_id = message.reply_to_message.from_user.id
    user = users_col.find_one({"user_id": target_user_id})
    if user:
        new_dia = user.get("dia", 0) + amount
        users_col.update_one({"user_id": target_user_id}, {"$set": {"dia": new_dia}})
    else:
        users_col.insert_one({"user_id": target_user_id, "usd": 10000.0, "dia": amount})
    bot.reply_to(message, f"✅ User ထံသို့ **{amount:,} Dia** ထည့်သွင်းပြီးပါပြီ။", parse_mode="Markdown")

# Game Menu - ပုံ ၁ ပါ အတိုင်း ခလုတ်ဒီဇိုင်းအတိအကျ
@bot.message_handler(commands=["game"])
def game_menu(message):
    user_name = message.from_user.first_name
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🎰 Slot Machine", callback_data="g_slot"),
        telebot.types.InlineKeyboardButton("🎲 Dice (Multiplayer)", callback_data="g_dice"),
        telebot.types.InlineKeyboardButton("🎳 Bowling", callback_data="g_bowling"),
        telebot.types.InlineKeyboardButton("🎯 Dart", callback_data="g_dart"),
        telebot.types.InlineKeyboardButton("⚽ Football", callback_data="g_football"),
        telebot.types.InlineKeyboardButton("🏀 Basketball", callback_data="g_basketball")
    )
    markup.add(telebot.types.InlineKeyboardButton("✊ ✌️ ✋ RPS (Diamond Game)", callback_data="g_rps"))
    
    bot.send_message(
        message.chat.id, 
        f"@{message.from_user.username or user_name} ကစားလိုသော ဂိမ်းအမျိုးအစားကို ရွေးချယ်ပါ -", 
        parse_mode="Markdown", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("g_"))
def select_game(call):
    g_type = call.data.split("_")[1]
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    bets = [1000, 5000, 10000, 50000, 100000, 500000]
    buttons = [telebot.types.InlineKeyboardButton(f"${b:,} USD", callback_data=f"bet_{g_type}_{b}") for b in bets]
    markup.add(*buttons)
    bot.edit_message_text(
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id, 
        text=f"🎮 Game 🕹️ ( **{g_type.upper()} BATTLE** )\n\n👤 {call.from_user.first_name}\n💰 လောင်းကြေးကို ရွေးချယ်ပါ -", 
        parse_mode="Markdown", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("bet_"))
def play_animation_game(call):
    data_parts = call.data.split("_")
    g_type = data_parts[1]
    bet = int(data_parts[2])
    
    user_id = call.from_user.id
    user = users_col.find_one({"user_id": user_id})
    current_usd = user.get("usd", 0) if user else 10000.0
    
    if current_usd < bet:
        bot.answer_callback_query(call.id, "❌ သင့်မှာ USD လက်ကျန် မလုံလောက်ပါ yaung!", show_alert=True)
        return
    
    new_usd = current_usd - bet
    users_col.update_one({"user_id": user_id}, {"$set": {"usd": new_usd}})
    
    bot.answer_callback_query(call.id, f"🎲 {bet:,} USD လောင်းပြီးပါပြီ။")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    emoji_map = {
        "dice": "🎲",
        "dart": "🎯",
        "basketball": "🏀",
        "football": "⚽",
        "bowling": "🎳"
    }
    
    if g_type in emoji_map:
        sent_msg = bot.send_dice(call.message.chat.id, emoji=emoji_map[g_type])
        time.sleep(3.5)
        dice_value = sent_msg.dice.value
        
        is_win = False
        multiplier = 2
        if g_type == "dice" and dice_value >= 4: is_win = True
        elif g_type == "dart" and dice_value >= 4: is_win = True
        elif g_type in ["basketball", "football"] and dice_value >= 3: is_win = True
        elif g_type == "bowling" and dice_value >= 5: is_win = True
            
        if is_win:
            win_amt = bet * multiplier
            final_usd = new_usd + win_amt
            users_col.update_one({"user_id": user_id}, {"$set": {"usd": final_usd}})
            result_text = (
                f"⚽ ရလဒ်: {dice_value}\n"
                f"🎉 အနိုင်ရရှိပါပြီ!\n"
                f"💰 အသာတင်း: +{win_amt:,.0f} USD\n"
                f"💵 လက်ကျန်ငွေ: `${final_usd:,.0f} USD`"
            )
        else:
            result_text = (
                f"⚽ ရလဒ်: {dice_value}\n"
                f"💔 ရှုံးပါသည်!\n"
                f"💸 အသာတင်း: -{bet:,.0f} USD\n"
                f"💵 လက်ကျန်ငွေ: `${new_usd:,.0f} USD`"
            )
        bot.send_message(call.message.chat.id, result_text, parse_mode="Markdown")
        
    elif g_type == "slot":
        symbols = ["🍇", "7", "BAR", "🍋", "🔔"]
        s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
        res = f"{s1} | {s2} | {s3}"
        if s1 == s2 == s3:
            win_amt = bet * 5
            final_usd = new_usd + win_amt
            users_col.update_one({"user_id": user_id}, {"$set": {"usd": final_usd}})
            bot.send_message(call.message.chat.id, f"🎰 {res}\n\n🎉 yaung နိုင်သွားပါပြီ! +{win_amt:,.0f} USD (လက်ကျန်: ${final_usd:,.0f} USD)")
        else:
            bot.send_message(call.message.chat.id, f"🎰 {res}\n\n💔 yaung ရှုံးပါသည်! (-{bet:,.0f} USD, လက်ကျန်: ${new_usd:,.0f} USD)")
            
    elif g_type == "rps":
        choices = ["ကျောက်ခဲ ✊",္ "ခရု ✌️", "စက္ကူ ✋"]
        bot.send_message(call.message.chat.id, f"✊ ✌️ ✋ RPS ဂိမ်းအတွက် yaung လောင်းကြေး ${bet:,} USD တင်ပြီးပါပြီ။ (နောက်ထပ် update ဆက်လုပ်ပေးပါမည်)")

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    try:
        bot.remove_webhook()
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Error: {e}")
