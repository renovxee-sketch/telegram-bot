import os
import telebot
from flask import Flask
from threading import Thread

TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Game Bot is running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

@bot.message_handler(commands=["start"])
def start(message):
    user_name = message.from_user.first_name  # user ရဲ့ နာမည်ကို ယူရန်
    bot_user_name = bot.get_me().username
    
    markup = telebot.types.InlineKeyboardMarkup()
    group_button = telebot.types.InlineKeyboardButton(
        "➕ Add Me To Your Group", 
        url=f"https://t.me/{bot_user_name}?startgroup=true"
    )
    markup.add(group_button)
    
    # User ရဲ့ နာမည်ကို နှုတ်ဆက်စာထဲမှာ ထည့်သွင်းပေးခြင်း
    welcome_text = (
        f"မင်္ဂလာပါ *{user_name}* (yaung) ရေ! 👋\n\n"
        "Bot က အောင်မြင်စွာ အလုပ်လုပ်နေပါပြီ။ 🚀\n"
        "ဂိမ်းတွေ ကစားချင်ရင် command တွေ သုံးနိုင်ပြီး၊ Group ထဲ ထည့်ချင်ရင် အောက်ကခလုတ်ကို နှိပ်ပါ -"
    )
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode="Markdown",
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
    t = Thread(target=run)
    t.start()
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    bot.infinity_polling()
