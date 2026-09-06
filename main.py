@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Player"

    # လူသစ်အတွက်သာ Welcome Bonus
    is_new_user = user_id not in user_balances

    if is_new_user:
        user_balances[user_id] = {
            "usd": 10000,
            "dia": 500
        }

        save_balances()

        welcome_bonus = """
🎁 NEW PLAYER BONUS

💵 USD +$10,000
💎 Diamonds +500

🎉 စတင်ကစားဖို့ အခမဲ့ဆု ရရှိပါပြီ!
"""
    else:
        welcome_bonus = ""

    usd = user_balances[user_id]["usd"]
    dia = user_balances[user_id]["dia"]

    text = f"""
👋 မင်္ဂလာပါ {first_name}!

🎮 အပျော်တန်း Game ကစားတဲ့ Bot မှ
ကြိုဆိုပါတယ်!

💎 Diamonds: {dia:,} 💎
💵 USD Balance: ${usd:,} USD

👇 အောက်ပါ Button ကို နှိပ်ပြီး
သင့် Group ထဲသို့ Bot ကို ထည့်သွင်းနိုင်ပါတယ်!
"""

    if welcome_bonus:
        text += "\n" + welcome_bonus

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "➕ Add Me Your GP",
            url="https://t.me/Ruifineshyt_bot?startgroup=true"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "🎮 Game Menu",
            callback_data="game_menu"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=keyboard
    )
