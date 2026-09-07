import os
import telebot
from flask import Flask
from threading import Thread

# Bot Token ကို Environment Variable ကနေ ယူပါတယ် (သို့မဟုတ် တိုက်ရိုက်ထည့်လို့ရပါတယ်)
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

# Flask server (Render မှာ Web Service အဖြစ် run နေချိန် Port ချိတ်ဆက်ဖို့အတွက်ပါ)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Port 8080 နဲ့ server ပေါ်မှာ run မယ်
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# /start command အတွက် 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါyaung! Bot က အဆင်သင့် ဖြစ်ပါပြီခင်ဗျ။")

# အခြား စာသားများအတွက်
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == "__main__":
    # Render အတွက် keep_alive ကို ဖွင့်ထားပေးပါ
    keep_alive()
    
    # Bot ကို အရင်ဟောင်းတွေပြတ်တောက်အောင် remove_webhook လုပ်ပြီးမှ infinity_polling စတင်ပါ
    try:
        bot.remove_webhook()
        print("Bot is starting polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Error: {e}")
