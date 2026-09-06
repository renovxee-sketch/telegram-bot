import os
import telebot
from flask import Flask
from threading import Thread

# Bot Token ထည့်ရန် (Render ရဲ့ Environment Variables ထဲမှာ BOT_TOKEN ထည့်ပေးရပါမယ်)
TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
bot = telebot.TeleBot(TOKEN)

# Render မှာ ဝဘ်ဆేవား အလုပ်လုပ်စေရန် (Port error မတက်အောင်)
app = Flask('')

@app.route('/')
def home():
    return "Game Bot is running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# /start နှိပ်ရင် Group ထဲထည့်မယ့်ခလုတ်ပါ ပေါ်လာစေရန်
@bot.message_handler(commands=["start"])
def start(message):
    bot_user_name = bot.get_me().username
    markup = telebot.types.InlineKeyboardMarkup()
    # Group ထဲ တိုက်ရိုက်ထည့်နိုင်သော လင့်ခ်ခလုတ်
    group_button = telebot.types.InlineKeyboardButton(
        "➕ Add Me To Your Group", 
        url=f"https://t.me/{bot_user_name}?startgroup=true"
    )
    markup.add(group_button)
    
    bot.send_message(
        message.chat.id, 
        "မင်္ဂလာပါ yaung! 🎮 ဒီ Bot ကနေ ဂိမ်းကစားလို့ရပါတယ်။ Group ထဲထည့်ချင်ရင် အောက်ကခလုတ်ကို နှိပ်ပါ -", 
        reply_markup=markup
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
def slot(message):
    bot.send_dice(message.chat.id, emoji='🎰')

@bot.message_handler(commands=["dart"])
def dart(message):
    bot.send_dice(message.chat.id, emoji='🎯')

if __name__ == "__main__":
    # Flask ဆာဗာကို Background မှာ အလုပ်လုပ်စေရန်
    t = Thread(target=run)
    t.start()
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    bot.infinity_polling()
