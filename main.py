import os
import telebot
import threading
from flask import Flask

# Balance system ကို ချိတ်ခြင်း
from balance import register_balance_handlers


# =========================
# BOT TOKEN
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")


# =========================
# TELEGRAM BOT
# =========================

bot = telebot.TeleBot(BOT_TOKEN)


# =========================
# BALANCE.PY ချိတ်ခြင်း
# =========================

register_balance_handlers(bot)


# =========================
# FLASK
# =========================

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!"


def run_flask():

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================
# START BOT
# =========================

if __name__ == "__main__":

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    print("Bot is running...")

    bot.remove_webhook()

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
