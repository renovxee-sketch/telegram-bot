from telebot import types
from database import get_user, update_balance


# ==========================================
# Pending Gift
# ==========================================

pending_gifts = {}


def money(value):
    return f"{int(value):,}"


# ==========================================
# Confirm / Cancel Keyboard
# ==========================================

def create_confirm_keyboard(key):

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(
            "✅ CONFIRM",
            callback_data=f"gift_confirm:{key}"
        ),
        types.InlineKeyboardButton(
            "❌ CANCEL",
            callback_data=f"gift_cancel:{key}"
        )
    )

    return markup


# ==========================================
# Gift Handlers
# ==========================================

def register_gift_handlers(bot):

    # ==========================================
    # /giftusd
    # ==========================================

    @bot.message_handler(commands=["giftusd"])
    def gift_usd(message):

        if not message.reply_to_message:

            bot.reply_to(
                message,
                "🎁 <b>USD GIFT</b>\n\n"
                "💵 Gift ပေးမယ့်သူရဲ့ message ကို Reply လုပ်ပါ။\n\n"
                "အသုံးပြုပုံ\n"
                "➜ <code>/giftusd 1000</code>",
                parse_mode="HTML"
            )

            return

        parts = message.text.split()

        if len(parts) != 2:

            bot.reply_to(
                message,
                "❌ <b>Amount မှားနေပါတယ်!</b>\n\n"
                "ဥပမာ ➜ <code>/giftusd 1000</code>",
                parse_mode="HTML"
            )

            return

        try:
            amount = int(parts[1])

        except ValueError:

            bot.reply_to(
                message,
                "❌ Amount ကို နံပါတ်နဲ့ပဲ ထည့်ပါ။"
            )

            return

        if amount <= 0:

            bot.reply_to(
                message,
                "❌ Amount က 0 ထက်ကြီးရပါမယ်။"
            )

            return

        sender = message.from_user
        receiver = message.reply_to_message.from_user

        if receiver.is_bot:

            bot.reply_to(
                message,
                "❌ Bot ကို Gift ပေးလို့မရပါ။"
            )

            return

        if sender.id == receiver.id:

            bot.reply_to(
                message,
                "❌ ကိုယ့်ကိုယ်ကို Gift ပေးလို့မရပါ။"
            )

            return

        sender_data = get_user(sender)

        if not sender_data:

            bot.reply_to(
                message,
                "❌ Account မတွေ့ပါ။\n"
                "/start အရင်လုပ်ပါ။"
            )

            return

        balance = int(sender_data.get("usd", 0))

        if balance < amount:

            bot.reply_to(
                message,
                "💸 <b>USD မလုံလောက်ပါ!</b>\n\n"
                f"💵 လက်ကျန်: <b>${money(balance)}</b>",
                parse_mode="HTML"
            )

            return

        # Receiver account ရှိအောင် ဖန်တီး/Update
        get_user(receiver)

        key = f"{message.chat.id}_{message.message_id}"

        pending_gifts[key] = {
            "type": "usd",
            "amount": amount,
            "sender_id": sender.id,
            "receiver_id": receiver.id,
            "sender_name": sender.first_name or "User",
            "receiver_name": receiver.first_name or "User"
        }

        bot.reply_to(
            message,
            "🎁 <b>USD GIFT</b>\n\n"
            f"👤 From: <b>{sender.first_name or 'User'}</b>\n"
            f"👤 To: <b>{receiver.first_name or 'User'}</b>\n\n"
            f"💵 Amount: <b>${money(amount)} USD</b>\n\n"
            "⚡ Gift ပေးမယ်ဆိုရင်\n"
            "<b>CONFIRM</b> ကိုနှိပ်ပါ 👇",
            reply_markup=create_confirm_keyboard(key),
            parse_mode="HTML"
        )


    # ==========================================
    # /giftdia
    # ==========================================

    @bot.message_handler(commands=["giftdia"])
    def gift_dia(message):

        if not message.reply_to_message:

            bot.reply_to(
                message,
                "🎁 <b>DIA GIFT</b>\n\n"
                "💎 Gift ပေးမယ့်သူရဲ့ message ကို Reply လုပ်ပါ။\n\n"
                "အသုံးပြုပုံ\n"
                "➜ <code>/giftdia 100</code>",
                parse_mode="HTML"
            )

            return

        parts = message.text.split()

        if len(parts) != 2:

            bot.reply_to(
                message,
                "❌ <b>Amount မှားနေပါတယ်!</b>\n\n"
                "ဥပမာ ➜ <code>/giftdia 100</code>",
                parse_mode="HTML"
            )

            return

        try:
            amount = int(parts[1])

        except ValueError:

            bot.reply_to(
                message,
                "❌ Amount ကို နံပါတ်နဲ့ပဲ ထည့်ပါ။"
            )

            return

        if amount <= 0:

            bot.reply_to(
                message,
                "❌ Amount က 0 ထက်ကြီးရပါမယ်။"
            )

            return

        sender = message.from_user
        receiver = message.reply_to_message.from_user

        if receiver.is_bot:

            bot.reply_to(
                message,
                "❌ Bot ကို Gift ပေးလို့မရပါ။"
            )

            return

        if sender.id == receiver.id:

            bot.reply_to(
                message,
                "❌ ကိုယ့်ကိုယ်ကို Gift ပေးလို့မရပါ။"
            )

            return

        sender_data = get_user(sender)

        if not sender_data:

            bot.reply_to(
                message,
                "❌ Account မတွေ့ပါ။\n"
                "/start အရင်လုပ်ပါ။"
            )

            return

        balance = int(sender_data.get("dia", 0))

        if balance < amount:

            bot.reply_to(
                message,
                "💎 <b>DIA မလုံလောက်ပါ!</b>\n\n"
                f"💎 လက်ကျန်: <b>{money(balance)} DIA</b>",
                parse_mode="HTML"
            )

            return

        # Receiver account ရှိအောင် ဖန်တီး/Update
        get_user(receiver)

        key = f"{message.chat.id}_{message.message_id}"

        pending_gifts[key] = {
            "type": "dia",
            "amount": amount,
            "sender_id": sender.id,
            "receiver_id": receiver.id,
            "sender_name": sender.first_name or "User",
            "receiver_name": receiver.first_name or "User"
        }

        bot.reply_to(
            message,
            "🎁 <b>DIA GIFT</b>\n\n"
            f"👤 From: <b>{sender.first_name or 'User'}</b>\n"
            f"👤 To: <b>{receiver.first_name or 'User'}</b>\n\n"
            f"💎 Amount: <b>{money(amount)} DIA</b>\n\n"
            "⚡ Gift ပေးမယ်ဆိုရင်\n"
            "<b>CONFIRM</b> ကိုနှိပ်ပါ 👇",
            reply_markup=create_confirm_keyboard(key),
            parse_mode="HTML"
        )


    # ==========================================
    # CONFIRM
    # ==========================================

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("gift_confirm:")
    )
    def confirm_gift(call):

        key = call.data.replace(
            "gift_confirm:",
            "",
            1
        )

        if key not in pending_gifts:

            bot.answer_callback_query(
                call.id,
                "❌ ဒီ Gift Request မရှိတော့ပါ။",
                show_alert=True
            )

            return

        gift = pending_gifts[key]

        # Sender ပဲ Confirm လုပ်နိုင်
        if call.from_user.id != gift["sender_id"]:

            bot.answer_callback_query(
                call.id,
                "⚠️ ဒီ Gift ကို ပေးတဲ့သူသာ Confirm လုပ်နိုင်ပါတယ်!",
                show_alert=True
            )

            return

        sender_data = get_user(call.from_user)

        if not sender_data:

            bot.answer_callback_query(
                call.id,
                "❌ Account မတွေ့ပါ။",
                show_alert=True
            )

            pending_gifts.pop(key, None)

            return

        # Receiver account ကို သေချာရှိအောင်လုပ်
        receiver_data = get_user(
            bot.get_chat_member(
                call.message.chat.id,
                gift["receiver_id"]
            ).user
        )

        if not receiver_data:

            bot.answer_callback_query(
                call.id,
                "❌ Receiver Account မတွေ့ပါ။",
                show_alert=True
            )

            pending_gifts.pop(key, None)

            return

        amount = int(gift["amount"])


        # ==========================================
        # USD
        # ==========================================

        if gift["type"] == "usd":

            current_balance = int(
                sender_data.get("usd", 0)
            )

            if current_balance < amount:

                bot.answer_callback_query(
                    call.id,
                    "❌ USD Balance မလုံလောက်တော့ပါ!",
                    show_alert=True
                )

                pending_gifts.pop(key, None)

                return

            update_balance(
                gift["sender_id"],
                usd_change=-amount
            )

            update_balance(
                gift["receiver_id"],
                usd_change=amount
            )

            currency_text = (
                f"💵 <b>${money(amount)} USD</b>"
            )


        # ==========================================
        # DIA
        # ==========================================

        else:

            current_balance = int(
                sender_data.get("dia", 0)
            )

            if current_balance < amount:

                bot.answer_callback_query(
                    call.id,
                    "❌ DIA Balance မလုံလောက်တော့ပါ!",
                    show_alert=True
                )

                pending_gifts.pop(key, None)

                return

            update_balance(
                gift["sender_id"],
                dia_change=-amount
            )

            update_balance(
                gift["receiver_id"],
                dia_change=amount
            )

            currency_text = (
                f"💎 <b>{money(amount)} DIA</b>"
            )


        # Pending ဖျက်
        pending_gifts.pop(
            key,
            None
        )


        # ==========================================
        # Success
        # ==========================================

        bot.answer_callback_query(
            call.id,
            "✅ Gift Sent!"
        )

        try:

            bot.edit_message_text(
                "╔════════════════════╗\n"
                "      🎁 <b>GIFT SENT!</b>\n"
                "╚════════════════════╝\n\n"
                f"👤 From: <b>{gift['sender_name']}</b>\n"
                f"👤 To: <b>{gift['receiver_name']}</b>\n\n"
                f"💰 Sent: {currency_text}\n\n"
                "🎉 Gift ပေးပို့ပြီးပါပြီ!",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )

        except Exception:
            pass


    # ==========================================
    # CANCEL
    # ==========================================

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("gift_cancel:")
    )
    def cancel_gift(call):

        key = call.data.replace(
            "gift_cancel:",
            "",
            1
        )

        if key not in pending_gifts:

            bot.answer_callback_query(
                call.id,
                "❌ ဒီ Gift Request မရှိတော့ပါ။",
                show_alert=True
            )

            return

        gift = pending_gifts[key]

        if call.from_user.id != gift["sender_id"]:

            bot.answer_callback_query(
                call.id,
                "⚠️ ဒီ Gift ကို ပေးတဲ့သူသာ Cancel လုပ်နိုင်ပါတယ်!",
                show_alert=True
            )

            return

        pending_gifts.pop(
            key,
            None
        )

        bot.answer_callback_query(
            call.id,
            "❌ Gift Cancelled"
        )

        try:

            bot.edit_message_text(
                "╔════════════════════╗\n"
                "     ❌ <b>GIFT CANCELLED</b>\n"
                "╚════════════════════╝\n\n"
                "ဒီ Gift Transaction ကို\n"
                "Cancel လုပ်လိုက်ပါပြီ။",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )

        except Exception:
            pass
