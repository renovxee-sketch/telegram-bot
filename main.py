import os
import time

from telegram import Update, BotCommand
from telegram.error import Conflict
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from start import start

from balance import (
    balance,
    buy_usd_command,
    set_dia,
    set_usd,
    add_user_balance,
)

from game import (
    game_command,
    rpstop,
    callback_handler,
)

from gift import (
    giftdia,
    giftusd,
)

from cards import (
    get_card,
    search_card,
    add_card,
    delete_card,
    handle_numeric_id,
)


# ==============================
# CONFIG
# ==============================

# Token ကို code ထဲမှာ မရေးပါ။
# Render Environment Variables ထဲက BOT_TOKEN ကိုယူမယ်။
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError(
        "BOT_TOKEN မရှိပါ။ Render Environment Variables "
        "ထဲမှာ BOT_TOKEN ထည့်ထားပါ။"
    )

try:
    OWNER_ID = int(
        os.getenv("OWNER_ID", "8032394583")
    )
except ValueError:
    raise ValueError(
        "OWNER_ID သည် ဂဏန်းဖြစ်ရပါမည်။"
    )

OWNER_USERNAME = "Ruifineshyt"


# ==============================
# BOT COMMANDS
# ==============================

async def post_init(
    application: Application,
) -> None:

    commands = [
        BotCommand("start", "Bot စတင်ရန်"),
        BotCommand("game", "ဂိမ်းများ ကစားရန်"),
        BotCommand("balance", "လက်ကျန်ငွေ စစ်ရန်"),
        BotCommand("buyusd", "USD ဝယ်ရန်"),
        BotCommand("giftdia", "Diamond လက်ဆောင်ပေးရန်"),
        BotCommand("giftusd", "USD လက်ဆောင်ပေးရန်"),
        BotCommand("rpstop", "RPS အနိုင်ရစာရင်း"),
        BotCommand("card", "Card ရယူရန်"),
        BotCommand("searchcard", "Card ရှာရန်"),
    ]

    try:
        await application.bot.set_my_commands(commands)
        print("✅ Bot commands set successfully.")

    except Exception as e:
        print(f"⚠️ Command setup error: {e}")


# ==============================
# ERROR HANDLER
# ==============================

async def global_error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    error = context.error

    if isinstance(error, Conflict):
        print(
            "❌ 409 Conflict: "
            "Bot ကို တခြား instance တစ်ခုက run နေပါတယ်။"
        )
        return

    print(f"⚠️ Bot Error: {error}")

    if isinstance(update, Update):

        if update.callback_query:

            try:
                await update.callback_query.answer(
                    "⚠️ ခဏတာ အမှားဖြစ်သွားပါတယ်။",
                    show_alert=True,
                )
            except Exception:
                pass

        elif update.effective_message:

            try:
                await update.effective_message.reply_text(
                    "⚠️ ခဏတာ အမှားဖြစ်သွားပါတယ်။ "
                    "ပြန်ကြိုးစားပေးပါ။"
                )
            except Exception:
                pass


# ==============================
# CREATE BOT
# ==============================

def create_application() -> Application:

    app = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .post_init(post_init)
        .build()
    )

    # ==========================
    # BASIC COMMANDS
    # ==========================

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("game", game_command)
    )

    app.add_handler(
        CommandHandler("balance", balance)
    )

    app.add_handler(
        CommandHandler("buyusd", buy_usd_command)
    )

    # ==========================
    # OWNER COMMANDS
    # ==========================

    app.add_handler(
        CommandHandler("dia", set_dia)
    )

    app.add_handler(
        CommandHandler("usd", set_usd)
    )

    app.add_handler(
        CommandHandler("add", add_user_balance)
    )

    # ==========================
    # RPS
    # ==========================

    app.add_handler(
        CommandHandler("rpstop", rpstop)
    )

    # ==========================
    # GIFTS
    # ==========================

    app.add_handler(
        CommandHandler(
            "giftdia",
            giftdia,
            block=False,
        )
    )

    app.add_handler(
        CommandHandler(
            "giftusd",
            giftusd,
            block=False,
        )
    )

    # ==========================
    # CARDS
    # ==========================

    app.add_handler(
        CommandHandler("card", get_card)
    )

    app.add_handler(
        CommandHandler(
            "searchcard",
            search_card,
        )
    )

    app.add_handler(
        CommandHandler(
            "addcard",
            add_card,
        )
    )

    app.add_handler(
        CommandHandler(
            "delete",
            delete_card,
        )
    )

    # ==========================
    # NUMERIC ID
    # ==========================

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_numeric_id,
        )
    )

    # ==========================
    # INLINE BUTTONS
    # ==========================

    app.add_handler(
        CallbackQueryHandler(
            callback_handler,
            block=False,
        )
    )

    # ==========================
    # ERROR HANDLER
    # ==========================

    app.add_error_handler(
        global_error_handler
    )

    return app


# ==============================
# MAIN
# ==============================

def main():

    print("================================")
    print("🤖 Telegram Game Bot")
    print("================================")
    print("✅ BOT_TOKEN loaded from ENV")
    print(f"✅ OWNER_ID: {OWNER_ID}")
    print("🚀 Bot starting...")

    while True:

        try:

            app = create_application()

            app.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
            )

            break

        except Conflict:

            print(
                "❌ 409 Conflict ဖြစ်နေပါတယ်။ "
                "အခြား bot instance ကို ပိတ်ပါ။"
            )

            time.sleep(10)

        except KeyboardInterrupt:

            print("🛑 Bot stopped.")
            break

        except Exception as e:

            print(
                f"⚠️ Bot error: {e}"
            )

            print(
                "🔄 5 seconds အကြာမှာ "
                "ပြန်စမ်းပါမယ်..."
            )

            time.sleep(5)


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    main()
