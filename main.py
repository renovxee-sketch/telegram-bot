import os
import threading
import telebot
from flask import Flask

# =========================
# IMPORT ALL SYSTEM FILES
# =========================

from balance import register_balance_handlers
from game import register_game_handlers
from gift import register_gift_handlers
from start import register_start_handlers


# =========================
# BOT TOKEN
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")


# =========================
# CREATE TELEGRAM BOT
# =========================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)


# =========================
# REGISTER ALL HANDLERS
# =========================

register_start_handlers(bot)
register_balance_handlers(bot)
register_game_handlers(bot)
register_gift_handlers(bot)


# =========================
# FLASK SERVER
# =========================

app = Flask(__name__)


@app.route("/")
def home():
    return "🎰 Casino Bot is running!"


def run_flask():

    port = int(os.environ.get("PORT", 10000))

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

    print("🎰 Casino Bot is running...")

    # Webhook ဖျက်ပြီး Polling အသုံးပြုမယ်
    bot.remove_webhook()

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
