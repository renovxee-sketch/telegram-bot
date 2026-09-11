import time
from telebot import types
from database import get_user, update_balance


def money(value):
    return f"{int(value):,}"


def mention_user(user):
    name = user.first_name or "User"
    return f'<a href="tg://user?id={user.id}">{name}</a>'


# =========================
# BET BUTTONS
# =========================

def create_bet_keyboard(owner_id):

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(
            "💵 10 USD",
            callback_data=f"slot_bet:{owner_id}:10"
        ),
        types.InlineKeyboardButton(
            "💵 100 USD",
            callback_data=f"slot_bet:{owner_id}:100"
        )
    )

    markup.row(
        types.InlineKeyboardButton(
            "💵 1K USD",
            callback_data=f"slot_bet:{owner_id}:1000"
        ),
        types.InlineKeyboardButton(
            "💵 5K USD",
            callback_data=f"slot_bet:{owner_id}:5000"
        )
    )

    markup.row(
        types.InlineKeyboardButton(
            "💵 10K USD",
            callback_data=f"slot_bet:{owner_id}:10000"
        ),
        types.InlineKeyboardButton(
            "💵 100K USD",
            callback_data=f"slot_bet:{owner_id}:100000"
        )
    )

    markup.row(
        types.InlineKeyboardButton(
            "💵 300K USD",
            callback_data=f"slot_bet:{owner_id}:300000"
        ),
        types.InlineKeyboardButton(
            "💵 500K USD",
            callback_data=f"slot_bet:{owner_id}:500000"
        )
    )

    # 1M တစ်ခုတည်း — အရှည်ကြီး
    markup.row(
        types.InlineKeyboardButton(
            "💵 1M USD",
            callback_data=f"slot_bet:{owner_id}:1000000"
        )
    )

    return markup


# =========================
# PLAY BUTTON
# =========================

def create_play_keyboard(owner_id):

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🎰 PLAY SLOT",
            callback_data=f"slot_play:{owner_id}"
        )
    )

    return markup


# =========================
# SLOT GAME
# =========================

def register_game_handlers(bot):

    @bot.message_handler(commands=["game"])
    def game_command(message):

        user = message.from_user

        text = (
            "🎰 <b>CASINO SLOT</b>\n\n"
            f"👤 {mention_user(user)}\n"
            f"💵 {money(get_user(user).get('usd', 0))} USD  "
            f"💎 {money(get_user(user).get('dia', 0))} DIA\n\n"
            "🍀 ကံစမ်းပြီး ဆော့လိုက်ပါ!"
        )

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=create_play_keyboard(user.id)
        )


    # =========================
    # PLAY SLOT
    # =========================

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("slot_play:")
    )
    def play_slot(call):

        owner_id = int(call.data.split(":")[1])

        if call.from_user.id != owner_id:

            bot.answer_callback_query(
                call.id,
                "🚫 ဒီ Game က မင်းအတွက်မဟုတ်ပါဘူး။ /game ကို ကိုယ်တိုင်နှိပ်ပြီး Game စပါ။",
                show_alert=True
            )

            return

        bot.answer_callback_query(call.id)

        try:
            bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
        except Exception:
            pass

        user = call.from_user

        text = (
            "🎰 <b>CASINO SLOT</b>\n\n"
            f"👤 {mention_user(user)}\n\n"
            "💵 <b>Bet Amount ရွေးပါ</b>"
        )

        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=create_bet_keyboard(owner_id)
        )


    # =========================
    # BET
    # =========================

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("slot_bet:")
    )
    def slot_bet(call):

        parts = call.data.split(":")

        if len(parts) != 3:
            bot.answer_callback_query(
                call.id,
                "❌ Invalid game.",
                show_alert=True
            )
            return

        owner_id = int(parts[1])
        bet = int(parts[2])

        # Only game owner can play
        if call.from_user.id != owner_id:

            bot.answer_callback_query(
                call.id,
                "🚫 ဒီ Game က မင်းအတွက်မဟုတ်ပါဘူး။ /game ကို ကိုယ်တိုင်နှိပ်ပြီး Game စပါ။",
                show_alert=True
            )

            return

        user = get_user(call.from_user)

        if not user:

            bot.answer_callback_query(
                call.id,
                "❌ User account မတွေ့ပါဘူး။ /start အရင်လုပ်ပါ။",
                show_alert=True
            )

            return

        balance = int(user.get("usd", 0))

        if balance < bet:

            bot.answer_callback_query(
                call.id,
                f"❌ လက်ကျန် USD မလုံလောက်ပါဘူး။\nလက်ကျန်: {money(balance)} USD",
                show_alert=True
            )

            return

        # Deduct bet first
        update_balance(
            owner_id,
            usd_change=-bet
        )

        bot.answer_callback_query(
            call.id,
            f"🎰 {money(bet)} USD Spin လုပ်နေပါပြီ..."
        )

        # Telegram real slot animation
        slot_message = bot.send_dice(
            call.message.chat.id,
            emoji="🎰"
        )

        # Wait for animation
        time.sleep(4)

        dice_value = slot_message.dice.value

        # Telegram slot decoding
        value = dice_value - 1

        left = value & 3
        middle = (value >> 2) & 3
        right = (value >> 4) & 3

        symbols = {
            0: "BAR",
            1: "🍇",
            2: "🍋",
            3: "7️⃣"
        }

        result = [
            symbols[left],
            symbols[middle],
            symbols[right]
        ]

        a, b, c = result

        multiplier = 0

        # =========================
        # SPECIAL WINS
        # =========================

        if result == ["7️⃣", "7️⃣", "7️⃣"]:
            multiplier = 30

        elif result == ["BAR", "BAR", "BAR"]:
            multiplier = 10

        elif result in [
            ["7️⃣", "7️⃣", "🍇"],
            ["🍇", "7️⃣", "7️⃣"],
            ["7️⃣", "7️⃣", "BAR"]
        ]:
            multiplier = 3

        # Other 3 identical symbols
        elif a == b == c:
            multiplier = 5

        # Two matching = no win
        else:
            multiplier = 0

        win_amount = bet * multiplier

        if multiplier > 0:

            update_balance(
                owner_id,
                usd_change=win_amount
            )

            final_user = get_user(call.from_user)
            new_balance = int(final_user.get("usd", 0))

            result_text = (
                "🎉 <b>YOU WIN!</b> 🎉\n\n"
                f"🎰 Result: <b>{a} | {b} | {c}</b>\n\n"
                f"💵 Bet: {money(bet)} USD\n"
                f"🔥 Multiplier: <b>{multiplier}x</b>\n"
                f"💰 Win: <b>+{money(win_amount)} USD</b>\n\n"
                f"💳 Balance: <b>{money(new_balance)} USD</b>"
            )

        else:

            final_user = get_user(call.from_user)
            new_balance = int(final_user.get("usd", 0))

            result_text = (
                "😢 <b>YOU LOSE!</b>\n\n"
                f"🎰 Result: <b>{a} | {b} | {c}</b>\n\n"
                f"💸 Loss: <b>-{money(bet)} USD</b>\n"
                f"💳 Balance: <b>{money(new_balance)} USD</b>"
            )

        # Reply to slot animation
        bot.reply_to(
            slot_message,
            result_text,
            reply_markup=create_bet_keyboard(owner_id)
        )
