import time
from telebot import types
from database import get_user, update_balance


# ==========================================
# Money Format
# ==========================================

def money(value):
    return f"{int(value):,}"


# ==========================================
# User Mention
# ==========================================

def mention_user(user):

    name = user.first_name or "User"

    return f'<a href="tg://user?id={user.id}">{name}</a>'


# ==========================================
# Bet Keyboard
# ==========================================

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

    markup.row(
        types.InlineKeyboardButton(
            "💵 1M USD",
            callback_data=f"slot_bet:{owner_id}:1000000"
        )
    )

    return markup


# ==========================================
# Play Button
# ==========================================

def create_play_keyboard(owner_id):

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🎰 PLAY SLOT",
            callback_data=f"slot_play:{owner_id}"
        )
    )

    return markup


# ==========================================
# Game Handlers
# ==========================================

def register_game_handlers(bot):


    # ==========================================
    # /game
    # ==========================================

    @bot.message_handler(commands=["game"])
    def game_command(message):

        user = message.from_user
        user_data = get_user(user)

        usd = int(user_data.get("usd", 0))
        dia = int(user_data.get("dia", 0))

        text = (
            "🎰 <b>CASINO SLOT</b>\n\n"
            f"👤 {mention_user(user)}\n"
            f"💵 {money(usd)} USD  "
            f"💎 {money(dia)} DIA\n\n"
            "🍀 ကံစမ်းပြီး ဆော့လိုက်ပါ!"
        )

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=create_play_keyboard(user.id),
            parse_mode="HTML"
        )


    # ==========================================
    # PLAY SLOT
    # ==========================================

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("slot_play:")
    )
    def play_slot(call):

        owner_id = int(
            call.data.split(":")[1]
        )

        # Game Owner Protection
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
            reply_markup=create_bet_keyboard(owner_id),
            parse_mode="HTML"
        )


    # ==========================================
    # SLOT BET
    # ==========================================

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


        # ==========================================
        # Owner Protection
        # ==========================================

        if call.from_user.id != owner_id:

            bot.answer_callback_query(
                call.id,
                "🚫 ဒီ Game က မင်းအတွက်မဟုတ်ပါဘူး။ /game ကို ကိုယ်တိုင်နှိပ်ပြီး Game စပါ။",
                show_alert=True
            )

            return


        # ==========================================
        # Get User
        # ==========================================

        user = get_user(call.from_user)

        if not user:

            bot.answer_callback_query(
                call.id,
                "❌ User account မတွေ့ပါဘူး။ /start အရင်လုပ်ပါ။",
                show_alert=True
            )

            return


        balance = int(
            user.get("usd", 0)
        )


        # ==========================================
        # Balance Check
        # ==========================================

        if balance < bet:

            bot.answer_callback_query(
                call.id,
                f"❌ USD မလုံလောက်ပါ!\n\n"
                f"💵 လက်ကျန်: {money(balance)} USD",
                show_alert=True
            )

            return


        # ==========================================
        # Deduct Bet
        # ==========================================

        update_balance(
            owner_id,
            usd_change=-bet
        )


        bot.answer_callback_query(
            call.id,
            f"🎰 {money(bet)} USD Spin လုပ်နေပါပြီ..."
        )


        # ==========================================
        # Telegram Slot
        # ==========================================

        slot_message = bot.send_dice(
            call.message.chat.id,
            emoji="🎰"
        )


        # Telegram animation ပြီးအောင်စောင့်
        time.sleep(4)


        # ==========================================
        # Read Slot Result
        # ==========================================

        dice_value = slot_message.dice.value

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


        # ==========================================
        # Multiplier
        # ==========================================

        multiplier = 0


        # 777
        if result == [
            "7️⃣",
            "7️⃣",
            "7️⃣"
        ]:

            multiplier = 30


        # BAR BAR BAR
        elif result == [
            "BAR",
            "BAR",
            "BAR"
        ]:

            multiplier = 10


        # Special 3x
        elif result in [

            [
                "7️⃣",
                "7️⃣",
                "🍇"
            ],

            [
                "🍇",
                "7️⃣",
                "7️⃣"
            ],

            [
                "7️⃣",
                "7️⃣",
                "BAR"
            ]

        ]:

            multiplier = 3


        # Three Same Symbols
        elif a == b == c:

            multiplier = 5


        # Lose
        else:

            multiplier = 0


        # ==========================================
        # Win Amount
        # ==========================================

        win_amount = bet * multiplier


        # ==========================================
        # WIN
        # ==========================================

        if multiplier > 0:

            # Win amount add
            update_balance(
                owner_id,
                usd_change=win_amount
            )


            final_user = get_user(
                call.from_user
            )

            new_balance = int(
                final_user.get("usd", 0)
            )


            # အသားတင်အမြတ်
            net_profit = win_amount - bet


            # ==========================================
            # WIN MESSAGE
            # ==========================================

            result_text = (
                "╔════════════════════╗\n"
                "       🎉 <b>YOU WIN!</b>\n"
                "╚════════════════════╝\n\n"

                f"🎰 <b>ရလဒ်:</b> "
                f"{a} | {b} | {c}\n\n"

                "🎉 <b>နိုင်ပါပြီ!</b>\n"

                f"💰 <b>အသားတင်: "
                f"+{money(net_profit)} USD</b>\n\n"

                f"💳 လက်ကျန်: "
                f"<b>{money(new_balance)} USD</b>\n\n"

                "🍀 ကံကောင်းပါစေ!"
            )


        # ==========================================
        # LOSE
        # ==========================================

        else:

            final_user = get_user(
                call.from_user
            )

            new_balance = int(
                final_user.get("usd", 0)
            )


            # ရှုံးတဲ့အခါ အသားတင်အရှုံး = Bet
            net_loss = bet


            # ==========================================
            # LOSE MESSAGE
            # ==========================================

            result_text = (
                "╔════════════════════╗\n"
                "      😢 <b>YOU LOSE</b>\n"
                "╚════════════════════╝\n\n"

                f"🎰 <b>ရလဒ်:</b> "
                f"{a} | {b} | {c}\n\n"

                "😢 <b>ရှုံးသွားပါပြီ!</b>\n"

                f"💸 <b>အသားတင်: "
                f"-{money(net_loss)} USD</b>\n\n"

                f"💳 လက်ကျန်: "
                f"<b>{money(new_balance)} USD</b>\n\n"

                "🍀 နောက်တစ်ကြိမ် ကံကောင်းပါစေ!"
            )


        # ==========================================
        # Send Result
        # ==========================================

        bot.reply_to(
            slot_message,
            result_text,
            reply_markup=create_bet_keyboard(owner_id),
            parse_mode="HTML"
        )
