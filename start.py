from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_username = context.bot.username
    user_display = user.full_name if user.full_name else "yaung"
    
    text = (
        f"👋 **မင်္ဂလာပါ {user_display} (`{user.id}`)!**\n\n"
        f"🎮 **ဂိမ်းကစားရန် Bot** မှ ကြိုဆိုပါတယ်ဗျာ။\n\n"
        f"👇 အောက်ပါခလုတ်ကိုနှိပ်ပြီး Group ထဲသို့ ထည့်သွင်းနိုင်ပါသည်!"
    )
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{bot_username}?startgroup=true")]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_numeric_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # အခြား စာသားစစ်ဆေးစရာများအတွက်
    pass
