# ==================================================
# SLOT BUTTON - STEP 2
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data == "game_slot")
def slot_button(call):

    bot.answer_callback_query(call.id)

    keyboard = InlineKeyboardMarkup(row_width=4)

    keyboard.add(
        InlineKeyboardButton("10", callback_data="slot_bet_10"),
        InlineKeyboardButton("100", callback_data="slot_bet_100"),
        InlineKeyboardButton("1K", callback_data="slot_bet_1000"),
        InlineKeyboardButton("10K", callback_data="slot_bet_10000"),
        InlineKeyboardButton("100K", callback_data="slot_bet_100000"),
        InlineKeyboardButton("300K", callback_data="slot_bet_300000"),
        InlineKeyboardButton("500K", callback_data="slot_bet_500000"),
        InlineKeyboardButton("1M", callback_data="slot_bet_1000000")
    )

    bot.edit_message_text(
        "🎰 <b>SLOT MACHINE</b>\n\n"
        "💵 လောင်းကြေးပမာဏကို ရွေးပါ 👇",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
