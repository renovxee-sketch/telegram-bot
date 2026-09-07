import telebot

TOKEN = "8693511224:AAEImdw0hwtaBaL8miVut3rhkGE-o8ImHtQ"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name or "မိတ်ဆွေ"

    bot.reply_to(
        message,
        f"👋 မင်္ဂလာပါ {name} ရေ!\n\n"
        f"🤖 ကျွန်တော်တို့ရဲ့ Bot မှာ ကြိုဆိုပါတယ်။\n"
        f"✨ Bot ကို စတင်အသုံးပြုနိုင်ပါပြီ။"
    )

print("Bot is running...")
bot.infinity_polling()
