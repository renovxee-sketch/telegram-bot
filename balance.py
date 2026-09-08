from telebot import types
from database import get_user, update_balance


def money(value):
    return f"{int(value):,}"


def mention_user(user):
    name = user.first_name or "User"
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def register_balance_handlers(bot):

    # ==========================================
    # /BALANCE
    # ==========================================

    @bot.message_handler(commands=["balance"])
    def balance_command(message):

        user = get_user(message.from_user)

        text = (
            f"👤 {mention_user(message.from_user)}\n\n"
            "💰 YOUR BALANCE\n\n"
            f"💵 USD ┃ ${money(user.get('usd', 0))}\n"
            f"💎 DIA ┃ {money(user.get('dia', 0))}💎"
        )

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "💵 USD ဝယ်ယူရန်",
                callback_data="buy_usd_info"
            )
        )

        bot.reply_to(
            message,
            text,
            reply_markup=markup,
            parse_mode="HTML"
        )


    # ==========================================
    # USD BUY BUTTON
    # ==========================================

    @bot.callback_query_handler(
        func=lambda call: call.data == "buy_usd_info"
    )
    def buy_usd_info(call):

        bot.answer_callback_query(call.id)

        text = (
            "💵 <b>USD ဝယ်ရန်</b>\n\n"
            "💱 <b>လက်ရှိစျေးနှုန်း:</b>\n"
            "100 USD = 1💎\n\n"
            "📌 <code>/buyusd [USD amount]</code>\n"
            "ဟုရိုက်ပြီး 💎 DIA ဖြင့် USD ဝယ်နိုင်ပါတယ်။\n\n"
            "<i>Example:</i>\n"
            "<code>/buyusd 100</code>"
        )

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML"
        )


    # ==========================================
    # /BUYUSD
    # ==========================================

    @bot.message_handler(commands=["buyusd"])
    def buyusd_command(message):

        parts = message.text.split()

        # Amount မပါလျှင်
        if len(parts) < 2:

            bot.reply_to(
                message,
                "❌ အသုံးပြုပုံ:\n\n"
                "/buyusd 100"
            )

            return

        try:
            usd_amount = int(parts[1])

        except ValueError:

            bot.reply_to(
                message,
                "❌ USD amount မမှန်ပါ။"
            )

            return

        # Negative / Zero
        if usd_amount <= 0:

            bot.reply_to(
                message,
                "❌ Amount က 0 ထက်ကြီးရပါမယ်။"
            )

            return

        # 100 ရဲ့ ဆတိုးဖြစ်ရမယ်
        if usd_amount % 100 != 0:

            bot.reply_to(
                message,
                "❌ 100 USD ရဲ့ ဆတိုးပမာဏသာ ဝယ်နိုင်ပါတယ်။\n\n"
                "ဥပမာ:\n"
                "/buyusd 100\n"
                "/buyusd 500\n"
                "/buyusd 1000"
            )

            return

        # 100 USD = 1 DIA
        dia_needed = usd_amount // 100

        user = get_user(message.from_user)

        # DIA မလုံလောက်လျှင်
        if user.get("dia", 0) < dia_needed:

            bot.reply_to(
                message,
                "❌ <b>DIA မလုံလောက်ပါ။</b>\n\n"
                f"💎 လိုအပ်သော DIA ┃ {money(dia_needed)}💎\n"
                f"💎 လက်ရှိ DIA ┃ "
                f"{money(user.get('dia', 0))}💎",
                parse_mode="HTML"
            )

            return

        # Balance Update
        update_balance(
            message.from_user.id,
            usd_change=usd_amount,
            dia_change=-dia_needed
        )

        new_user = get_user(message.from_user)

        bot.reply_to(
            message,
            "✅ <b>USD ဝယ်ယူပြီးပါပြီ!</b>\n\n"
            f"💵 ဝယ်ယူသော USD ┃ "
            f"${money(usd_amount)}\n"
            f"💎 အသုံးပြုသော DIA ┃ "
            f"{money(dia_needed)}💎\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "💰 <b>YOUR BALANCE</b>\n\n"
            f"💵 USD ┃ "
            f"${money(new_user.get('usd', 0))}\n"
            f"💎 DIA ┃ "
            f"{money(new_user.get('dia', 0))}💎",
            parse_mode="HTML"
            )
