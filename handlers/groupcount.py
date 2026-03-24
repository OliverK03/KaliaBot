from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import get_group_total

async def groupcount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = get_group_total(str(update.effective_chat.id))
    await update.message.reply_text(f'Ryhmässä juotu yhteensä {total} kaliaa.')