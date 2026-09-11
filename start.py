from telebot import types
from database import users_collection


def register_start_handlers(bot):

    @bot.message_handler(commands=["start"])
    def start_command(message):

        user = message.from_user

        existing_user = users_collection.find_one(
            {"user_id": user.id}
        )

        # User အသစ်ဆိုရင် Bonus တစ်ကြိမ်ပဲပေးမယ်
        if not existing_user:

            users_collection.insert_one({
                "user_id": user.id,
                "name": user.first_name or "User",
                "username": user.username or "",
                "usd": 50000,
                "dia": 500,
                "welcome_bonus": True
            })

        else:

            # Balance ကို မထိဘဲ Name / Username ပဲ update
            users_collection.update_one(
                {"user_id": user.id},
                {
                    "$set": {
                        "name": user.first_name or "User",
                        "username": user.username or ""
                    }
                }
            )

        # MongoDB ထဲက လက်ရှိ balance ကိုယူ
        current_user = users_collection.find_one(
            {"user_id": user.id}
        )

        usd = int(current_user.get("usd", 0))
        dia = int(current_user.get("dia", 0))

        name = user.first_name or "User"

        text = (
            f"👋 မင်္ဂလာပါ <b>{name}</b> ({user.id})!\n\n"
            "🎮 ဂိမ်းကစားရန် Bot မှ ကြိုဆိုပါတယ်!\n\n"
            f"💎 Diamonds: {dia:,} 💎\n"
            f"💵 USD: ${usd:,} USD\n\n"
            "👇 အောက်ပါခလုတ်ကိုနှိပ်ပြီး Group ထဲသို့ "
            "ထည့်သွင်းနိုင်ပါသည်!"
        )

        markup = types.InlineKeyboardMarkup()

        # Add Group Button
        markup.add(
            types.InlineKeyboardButton(
                "➕  ADD ME TO YOUR GROUP  ➕",
                url="https://t.me/Ruifineshyt_bot?startgroup=true"
            )
        )

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=markup,
            parse_mode="HTML"
        )
