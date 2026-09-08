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

def create_bet_keyboard():

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton("💵 10 USD", callback_data="slot_bet:10"),
        types.InlineKeyboardButton("💵 100 USD", callback_data="slot_bet:100"),
        types.InlineKeyboardButton("💵 1K USD", callback_data="slot_bet:1000")
    )

    markup.row(
        types.InlineKeyboardButton("💵 5K USD", callback_data="slot_bet:5000"),
        types.InlineKeyboardButton("💵 10K USD", callback_data="slot_bet:10000"),
        types.InlineKeyboardButton("💵 100K USD", callback_data="slot_bet:100000")
    )

    markup.row(
        types.InlineKeyboardButton("💵 300K USD", callback_data="slot_b
