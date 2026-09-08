import os
import threading

import telebot
from flask import Flask

from balance import register_balance_handlers
from game import register_game_handlers
from gift import register_gift_handlers
from start import register_start_handlers


BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")


bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)


# Register handlers
register_start_handlers(bot)
register_balance_handlers(bot)
register_game_handlers(bot)
register_gift_handlers(bot)


# Flask app for Render
app = Flask(__name__)


@app.route("/")
def home():
    return "Casino Bot is Running!"


@app.route("/health")
def health():
    return "OK"


# Telegram Bot
def run_bot():
    print("🎰 Telegram Bot Starting...")

    bot.remove_webhook()

    bot.infinity_polling(
        skip_pending=True,
        timeout=20,
        long_polling_timeout=20
    )


# Start
if __name__ == "__main__":

    bot_thread = threading.Thread(
        target=run_bot,
        daemon=True
    )

    bot_thread.start()

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    print(f"🌐 Web Server starting on port {port}")

    app.run(
        host="0.0.0.0",
        port=port
    )
