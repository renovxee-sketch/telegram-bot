from telebot import types
from database import get_user, update_balance


# =========================
# MONEY FORMAT
# =========================

def money(value):
    return f"{int(value):,}"


def mention_user(user):
    name = user.first_name or "User"
    return f'<a href="tg://user?id={user.id}">{name}</a>'


# =========================
# REGISTER BALANCE HANDLERS
# =========================

def register_balance_handlers(bot):

    # =========================
    # /BALANCE
    # =========================

    @bot.message_handler(commands=["balance"])
    def balance_command(message):

        user = get_user(message.from_user)

        text = (
            "╔════════════════════════════╗\n"
            "       💰 YOUR BALANCE 💰\n"
            "╚════════════════════════════╝\n\n"
            f"👤 {mention_user(message.from_user)}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 USD ┃ ${money(user.get('usd', 0))}\n"
            f"💎 DIA ┃ {money(user.get('dia', 0))}💎\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )

        # USD ဝယ်ရန် Button
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


    # =========================
    # USD BUY BUTTON
    # =========================

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


    # =========================
    # /BUYUSD
    # =========================

    @bot.message_handler(commands=["buyusd"])
    def buy_usd_command(message):

        parts = message.text.split()

        # Amount မပါလျှင်
        if len(parts) != 2:

            bot.reply_to(
                message,
                "❌ <b>အသုံးပြုပုံမှားနေပါတယ်!</b>\n\n"
                "📌 <code>/buyusd [USD amount]</code>\n\n"
                "<i>Example:</i>\n"
                "<code>/buyusd 100</code>",
                parse_mode="HTML"
            )

            return

        # Number စစ်ခြင်း
        try:
            usd_amount = int(parts[1])

        except ValueError:

            bot.reply_to(
                message,
                "❌ USD Amount ကို ဂဏန်းဖြင့်သာ ရိုက်ထည့်ပါ။"
            )

            return

        # 0 / Negative
        if usd_amount <= 0:

            bot.reply_to(
                message,
                "❌ USD Amount သည် 0 ထက် ကြီးရပါမယ်။"
            )

            return

        # 100 ရဲ့ ဆတိုးသာ ဝယ်နိုင်
        if usd_amount % 100 != 0:

            bot.reply_to(
                message,
                "❌ <b>100 USD ရဲ့ ဆတိုးပမာဏသာ ဝယ်နိုင်ပါတယ်!</b>\n\n"
                "ဥပမာ:\n"
                "💵 /buyusd 100\n"
                "💵 /buyusd 500\n"
                "💵 /buyusd 1000",
                parse_mode="HTML"
            )

            return

        # =========================
        # PRICE
        # 100 USD = 1 DIA
        # =========================

        dia_needed = usd_amount // 100

        user = get_user(message.from_user)

        current_dia = user.get("dia", 0)

        # DIA မလုံလောက်
        if current_dia < dia_needed:

            bot.reply_to(
                message,
                "❌ <b>DIA Balance မလုံလောက်ပါ!</b>\n\n"
                f"💎 လိုအပ်သော DIA ┃ {money(dia_needed)}💎\n"
                f"💎 လက်ရှိ DIA ┃ {money(current_dia)}💎",
                parse_mode="HTML"
            )

            return

        # =========================
        # UPDATE BALANCE
        # =========================

        update_balance(
            message.from_user.id,
            usd_change=usd_amount,
            dia_change=-dia_needed
        )

        # Updated Balance
        updated_user = get_user(message.from_user)

        # =========================
        # SUCCESS
        # =========================

        text = (
            "✅ <b>USD ဝယ်ယူမှု အောင်မြင်ပါသည်!</b>\n\n"
            f"💵 ဝယ်ယူသော USD ┃ ${money(usd_amount)}\n"
            f"💎 အသုံးပြုသော DIA ┃ {money(dia_needed)}💎\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💰 <b>YOUR NEW BALANCE</b>\n\n"
            f"💵 USD ┃ ${money(updated_user.get('usd', 0))}\n"
            f"💎 DIA ┃ {money(updated_user.get('dia', 0))}💎\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )

        bot.reply_to(
            message,
            text,
            parse_mode="HTML"
        )
