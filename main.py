import telebot
from telebot import types

TOKEN = "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user

    # Telegram Account Name
    name = user.first_name or "Friend"

    # Username ရှိရင် @username၊ မရှိရင် Name ကိုသုံးမယ်
    if user.username:
        display_name = f"@{user.username}"
    else:
        display_name = name

    # Inline Button
    markup = types.InlineKeyboardMarkup()

    add_group_button = types.InlineKeyboardButton(
        "➕ Add Me Your Group",
        url=f"https://t.me/{bot.get_me().username}?startgroup=true"
    )

    markup.add(add_group_button)

    # Welcome Message
    welcome_text = f"""
👋 မင်္ဂလာပါ {display_name}!

✨ Bot မှာ ကြိုဆိုပါတယ်။

🤖 ဒီ Bot ကို Group ထဲထည့်ပြီး
အဆင်ပြေပြေ အသုံးပြုနိုင်ပါတယ်။

👇 အောက်က Button ကိုနှိပ်ပြီး
Bot ကို သင့် Group ထဲထည့်လိုက်ပါ။
"""

    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup
    )


print("🤖 Bot is running...")

bot.infinity_polling()
