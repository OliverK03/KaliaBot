from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from utils.storage import increment_count
from utils.storage import pyha_increment

async def pyha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo or not update.message.caption:
        print("Ignoring /pyha because it was not sent in a photo caption.")
        return

    if update.effective_message:
        try:
            await update.effective_message.set_reaction("❤")
        except TelegramError as exc:
            print(f"Could not set reaction: {exc}")

    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    increment_count(chat_id, user_id)
    pyha_increment(chat_id, user_id)
