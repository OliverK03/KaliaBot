from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import increment_count

async def kalia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    increment_count(chat_id, user_id)