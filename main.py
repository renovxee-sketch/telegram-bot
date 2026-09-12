import os
import asyncio
import logging
import traceback

from telegram import Update, BotCommand
from telegram.error import Conflict, TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError(
        "BOT_TOKEN မရှိပါ။ Render > Environment Variables "
        "မှာ BOT_TOKEN ထည့်ထားကြောင်း စစ်ပါ။"
    )

OWNER_ID = int(os.getenv("OWNER_ID", "8032394583"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "Ruifineshyt")


# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================
# BOT COMMANDS
# =========================

async def post_init(application: Application):
    commands = [
        BotCommand("start", "Bot စတင်ရန်"),
        BotCommand("game", "Game Menu"),
        BotCommand("balance", "Balance ကြည့်ရန်"),
        BotCommand("buyusd", "USD ဝယ်ရန်"),
        BotCommand("giftdia", "Diamond လွှဲရန်"),
        BotCommand("giftusd", "USD လွှဲရန်"),
        BotCommand("searchcard", "Card ရှာရန်"),
        BotCommand("card", "Card ကြည့်ရန်"),
    ]

    await application.bot.set_my_commands(commands)

    logger.info("Bot commands loaded successfully.")


# =========================
# ERROR HANDLER
# =========================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):
    error = context.error

    logger.error(
        "Exception while handling an update:",
        exc_info=(
            type(error),
            error,
            error.__traceback__
        )
    )

    # Telegram polling conflict
    if isinstance(error, Conflict):
        logger.error(
            "409 Conflict ဖြစ်နေပါတယ်။ "
            "Bot instance တစ်ခုထက်ပိုပြီး polling လုပ်နေပါတယ်။"
        )
        return

    # Other Telegram errors
    if isinstance(error, TelegramError):
        logger.error(
            "Telegram error: %s",
            error
        )
        return

    logger.error(
        "Unknown error: %s",
        traceback.format_exc()
    )


# =========================
# APPLICATION
# =========================

def build_application():

    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    # ---------------------------------
    # START
    # ---------------------------------

    from start import start_command
    from start import handle_numeric_id

    application.add_handler(
        CommandHandler("start", start_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_numeric_id
        )
    )

    # ---------------------------------
    # BALANCE
    # ---------------------------------

    from balance import (
        balance_command,
        buyusd_command,
        dia_command,
        usd_command,
        add_command,
    )

    application.add_handler(
        CommandHandler("balance", balance_command)
    )

    application.add_handler(
        CommandHandler("buyusd", buyusd_command)
    )

    application.add_handler(
        CommandHandler("dia", dia_command)
    )

    application.add_handler(
        CommandHandler("usd", usd_command)
    )

    application.add_handler(
        CommandHandler("add", add_command)
    )

    # ---------------------------------
    # GAME
    # ---------------------------------

    from game import (
        game_command,
        game_callback,
    )

    application.add_handler(
        CommandHandler("game", game_command)
    )

    # ---------------------------------
    # GIFT
    # ---------------------------------

    from gift import (
        giftdia_command,
        giftusd_command,
        gift_callback,
    )

    application.add_handler(
        CommandHandler("giftdia", giftdia_command)
    )

    application.add_handler(
        CommandHandler("giftusd", giftusd_command)
    )

    # ---------------------------------
    # CARDS
    # ---------------------------------

    from cards import (
        searchcard_command,
        card_command,
        addcard_command,
        deletecard_command,
        card_callback,
    )

    application.add_handler(
        CommandHandler("searchcard", searchcard_command)
    )

    application.add_handler(
        CommandHandler("card", card_command)
    )

    application.add_handler(
        CommandHandler("addcard", addcard_command)
    )

    application.add_handler(
        CommandHandler("delete", deletecard_command)
    )

    # ---------------------------------
    # CALLBACKS
    # ---------------------------------

    application.add_handler(
        CallbackQueryHandler(game_callback, pattern=r"^(game_|mpdice_|mprps_|bet_|)")
    )

    application.add_handler(
        CallbackQueryHandler(gift_callback, pattern=r"^gift_")
    )

    application.add_handler(
        CallbackQueryHandler(card_callback, pattern=r"^(card_|draw_card|back_card)")
    )

    # ---------------------------------
    # ERROR
    # ---------------------------------

   
