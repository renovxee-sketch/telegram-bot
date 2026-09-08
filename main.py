import os
import telebot
import threading
from flask import Flask

# =========================
# IMPORT OTHER PY FILES
# =========================

from balance import register_balance_handlers
from game import register_game_handlers
from gift import register_gift_handlers


# =========================
# BOT TOKEN
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")


# =========================
# TELEGRAM BOT
# =========================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)


# =========================
# REGISTER ALL SYSTEMS
# =========================

register_balance_handlers(bot)
register_game_handlers(bot)
register_gift_handlers(bot)


# =========================
# FLASK WEB SERVER
# =========================

app = Flask(__name__)


@app.route("/")
def home():
    return "Casino Bot is running!"


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

    print("🎰 Casino Bot is running...")

    # Webhook ရှိနေရင် ဖျက်မယ်
    bot.remove_webhook()

    # Bot စတင်မယ်
    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
