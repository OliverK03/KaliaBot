from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import get_group_total
from utils.storage import get_group_pyhat

async def groupcount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = get_group_total(str(update.effective_chat.id))
    pyha_total = get_group_pyhat(str(update.effective_chat.id))
    await update.message.reply_text(f'Ryhmässä juotu yhteensä {total} kaliaa, joista pyhiä {pyha_total}.')