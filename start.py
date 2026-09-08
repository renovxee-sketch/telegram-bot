from telebot import types
from database import users_collection


def register_start_handlers(bot):

    @bot.message_handler(commands=["start"])
    def start_command(message):

        user = message.from_user

        # Database မှာ User ရှိ/မရှိ စစ်
        existing_user = users_collection.find_one(
            {"user_id": user.id}
        )

        # =========================
        # USER အသစ်
        # =========================

        if not existing_user:

            users_collection.insert_one({
                "user_id": user.id,
                "name": user.first_name or "User",
                "username": user.username or "",
                "usd": 20000,
                "dia": 500,
                "welcome_bonus": True
            })

            text = (
                "🎉 <b>WELCOME TO CASINO BOT!</b>\n\n"
                "🎁 <b>FREE START BONUS</b>\n\n"
                "💵 USD ┃ $20,000\n"
                "💎 DIA ┃ 500💎\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🍀 ကံကောင်းတဲ့ Casino Game တွေကို စတင်ကစားလိုက်ပါ!"
            )

        # =========================
        # USER အဟောင်း
        # =========================

        else:

            # Name / Username Update
            users_collection.update_one(
                {"user_id": user.id},
                {
                    "$set": {
                        "name": user.first_name or "User",
                        "username": user.username or ""
                    }
                }
            )

            text = (
                "🎰 <b>WELCOME BACK!</b>\n\n"
                "Casino မှာ ပြန်လည်ကစားနိုင်ပါပြီ 🍀"
            )

        # =========================
        # START MENU BUTTONS
        # =========================

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            row_width=2
        )

        markup.row(
            types.KeyboardButton("/balance"),
            types.KeyboardButton("/game")
        )

        markup.row(
            types.KeyboardButton("/giftusd"),
            types.KeyboardButton("/giftdia")
        )

        bot.reply_to(
            message,
            text,
            reply_markup=markup,
            parse_mode="HTML"
        )
