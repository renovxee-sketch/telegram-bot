from telebot import types
from database import get_user, update_balance


# Pending Gift များကို ခဏသိမ်းရန်
pending_gifts = {}


def money(value):
    return f"{int(value):,}"


def register_gift_handlers(bot):

    # ==========================================
    # /GIFTUSD
    # အသုံးပြုပုံ:
    # /giftusd amount
    # Reply လုပ်ပြီး သုံးရန်
    # ==========================================

    @bot.message_handler(commands=["giftusd"])
    def gift_usd(message):

        # Reply လုပ်ထားရမယ်
        if not message.reply_to_message:
            bot.reply_to(
                message,
                "❌ <b>အသုံးပြုပုံမှားနေပါတယ်!</b>\n\n"
                "💵 USD ပေးလိုသူကို Reply လုပ်ပြီး အသုံးပြုပါ။\n\n"
                "<code>/giftusd [amount]</code>\n\n"
                "ဥပမာ:\n"
                "User တစ်ယောက်ကို Reply → <code>/giftusd 1000</code>",
                parse_mode="HTML"
            )
            return

        parts = message.text.split()

        if len(parts) != 2:
            bot.reply_to(
                message,
                "❌ အသုံးပြုပုံ:\n"
                "<code>/giftusd 1000</code>",
                parse_mode="HTML"
            )
            return

        try:
            amount = int(parts[1])
        except ValueError:
            bot.reply_to(
                message,
                "❌ Amount မှန်ကန်စွာ ရိုက်ထည့်ပါ။"
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

        # Bot ကို Gift မပေးနိုင်
        if receiver.is_bot:
            bot.reply_to(
                message,
                "❌ Bot ကို Gift ပေးလို့မရပါ။"
            )
            return

        # ကိုယ့်ကိုယ်ကို မပေးနိုင်
        if sender.id == receiver.id:
            bot.reply_to(
                message,
                "❌ ကိုယ့်ကိုယ်ကို Gift ပေးလို့မရပါ။"
            )
            return

        sender_data = get_user(sender)

        if sender_data.get("usd", 0) < amount:
            bot.reply_to(
                message,
                "❌ <b>USD Balance မလုံလောက်ပါ!</b>\n\n"
                f"💵 လက်ရှိ USD ┃ ${money(sender_data.get('usd', 0))}",
                parse_mode="HTML"
            )
            return

        # Pending Gift သိမ်း
        key = f"{message.chat.id}_{message.message_id}"

        pending_gifts[key] = {
            "type": "usd",
            "amount": amount,
            "sender_id": sender.id,
            "receiver_id": receiver.id,
            "sender_name": sender.first_name or "User",
            "receiver_name": receiver.first_name or "User"
        }

        # Confirm / Cancel Buttons
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

        bot.reply_to(
            message,
            "🎁 <b>USD GIFT CONFIRMATION</b>\n\n"
            f"👤 From: {sender.first_name}\n"
            f"👤 To: {receiver.first_name}\n\n"
            f"💵 Amount: ${money(amount)} USD\n\n"
            "Gift ပေးရန် Confirm ကိုနှိပ်ပါ 👇",
            reply_markup=markup,
            parse_mode="HTML"
        )


    # ==========================================
    # /GIFTDIA
    # ==========================================

    @bot.message_handler(commands=["giftdia"])
    def gift_dia(message):

        if not message.reply_to_message:
            bot.reply_to(
                message,
                "❌ <b>အသုံးပြုပုံမှားနေပါတယ်!</b>\n\n"
                "💎 DIA ပေးလိုသူကို Reply လုပ်ပြီး အသုံးပြုပါ။\n\n"
                "<code>/giftdia [amount]</code>\n\n"
                "ဥပမာ:\n"
                "User တစ်ယောက်ကို Reply → <code>/giftdia 100</code>",
                parse_mode="HTML"
            )
            return

        parts = message.text.split()

        if len(parts) != 2:
            bot.reply_to(
                message,
                "❌ အသုံးပြုပုံ:\n"
                "<code>/giftdia 100</code>",
                parse_mode="HTML"
            )
            return

        try:
            amount = int(parts[1])
        except ValueError:
            bot.reply_to(
                message,
                "❌ Amount မှန်ကန်စွာ ရိုက်ထည့်ပါ။"
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

        # Bot ကို Gift မပေးနိုင်
        if receiver.is_bot:
            bot.reply_to(
                message,
                "❌ Bot ကို Gift ပေးလို့မရပါ။"
            )
            return

        # ကိုယ့်ကိုယ်ကို မပေးနိုင်
        if sender.id == receiver.id:
            bot.reply_to(
                message,
                "❌ ကိုယ့်ကိုယ်ကို Gift ပေးလို့မရပါ။"
            )
            return

        sender_data = get_user(sender)

        if sender_data.get("dia", 0) < amount:
            bot.reply_to(
                message,
                "❌ <b>DIA Balance မလုံလောက်ပါ!</b>\n\n"
                f"💎 လက်ရှိ DIA ┃ {money(sender_data.get('dia', 0))}💎",
                parse_mode="HTML"
            )
            return

        key = f"{message.chat.id}_{message.message_id}"

        pending_gifts[key] = {
            "type": "dia",
            "amount": amount,
            "sender_id": sender.id,
            "receiver_id": receiver.id,
            "sender_name": sender.first_name or "User",
            "receiver_name": receiver.first_name or "User"
        }

        # Confirm / Cancel Buttons
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

        bot.reply_to(
            message,
            "🎁 <b>DIA GIFT CONFIRMATION</b>\n\n"
            f"👤 From: {sender.first_name}\n"
            f"👤 To: {receiver.first_name}\n\n"
            f"💎 Amount: {money(amount)} DIA\n\n"
            "Gift ပေးရန် Confirm ကိုနှိပ်ပါ 👇",
            reply_markup=markup,
            parse_mode="HTML"
        )


    # ==========================================
    # CONFIRM
    # ==========================================

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("gift_confirm:")
    )
    def confirm_gift(call):

        key = call.data.replace("gift_confirm:", "")

        if key not in pending_gifts:
            bot.answer_callback_query(
                call.id,
                "❌ ဒီ Gift Request မရှိတော့ပါ။",
                show_alert=True
            )
            return

        gift = pending_gifts[key]

        # Gift ပေးမယ့်သူပဲ Confirm လုပ်နိုင်
        if call.from_user.id != gift["sender_id"]:
            bot.answer_callback_query(
                call.id,
                "⚠️ ဒီ Gift ကို ဖန်တီးထားတဲ့သူသာ Confirm လုပ်နိုင်ပါတယ်!",
                show_alert=True
            )
            return

        sender_data = get_user(call.from_user)

        amount = gift["amount"]

        # ==========================================
        # USD GIFT
        # ==========================================

        if gift["type"] == "usd":

            if sender_data.get("usd", 0) < amount:

                bot.answer_callback_query(
                    call.id,
                    "❌ USD Balance မလုံလောက်တော့ပါ!",
                    show_alert=True
                )

                pending_gifts.pop(key, None)
                return

            # Sender USD လျှော့
            update_balance(
                gift["sender_id"],
                usd_change=-amount
            )

            # Receiver USD တိုး
            update_balance(
                gift["receiver_id"],
                usd_change=amount
            )

            currency_text = f"💵 ${money(amount)} USD"

        # ==========================================
        # DIA GIFT
        # ==========================================

        else:

            if sender_data.get("dia", 0) < amount:

                bot.answer_callback_query(
                    call.id,
                    "❌ DIA Balance မလုံလောက်တော့ပါ!",
                    show_alert=True
                )

                pending_gifts.pop(key, None)
                return

            # Sender DIA လျှော့
            update_balance(
                gift["sender_id"],
                dia_change=-amount
            )

            # Receiver DIA တိုး
            update_balance(
                gift["receiver_id"],
                dia_change=amount
            )

            currency_text = f"💎 {money(amount)} DIA"

        # Pending Gift ဖျက်
        pending_gifts.pop(key, None)

        bot.answer_callback_query(
            call.id,
            "✅ Gift Successfully Sent!"
        )

        # Confirmation Message ပြောင်း
        try:

            bot.edit_message_text(
                "🎁 <b>GIFT SUCCESSFUL!</b>\n\n"
                f"👤 From: {gift['sender_name']}\n"
                f"👤 To: {gift['receiver_name']}\n\n"
                f"💰 Sent: {currency_text}\n\n"
                "✅ Gift ပေးပို့ပြီးပါပြီ!",
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

        key = call.data.replace("gift_cancel:", "")

        if key not in pending_gifts:

            bot.answer_callback_query(
                call.id,
                "❌ ဒီ Gift Request မရှိတော့ပါ။",
                show_alert=True
            )

            return

        gift = pending_gifts[key]

        # Gift ပေးတဲ့သူပဲ Cancel လုပ်နိုင်
        if call.from_user.id != gift["sender_id"]:

            bot.answer_callback_query(
                call.id,
                "⚠️ ဒီ Gift ကို ဖန်တီးထားတဲ့သူသာ Cancel လုပ်နိုင်ပါတယ်!",
                show_alert=True
            )

            return

        # Pending Gift ဖျက်
        pending_gifts.pop(key, None)

        bot.answer_callback_query(
            call.id,
            "❌ Gift Cancelled"
        )

        # Cancelled Message ပြောင်း
        try:

            bot.edit_message_text(
                "❌ <b>GIFT CANCELLED</b>\n\n"
                "ဒီ Gift Transaction ကို Cancel လုပ်လိုက်ပါ!",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )

        except Exception:
            pass
