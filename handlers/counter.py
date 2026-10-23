from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from utils.storage import increment_kalia_count


async def kalia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo or not update.message.caption:
        print("Ignoring /kalia because it was not sent in a photo caption.")
        return

    if update.effective_message:
        try:
            await update.effective_message.set_reaction("❤")
        except TelegramError as exc:
            print(f"Could not set reaction: {exc}")

    message = update.message
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    increment_kalia_count(
        chat_id,
        user_id,
        telegram_message_id=message.message_id,
        occurred_at=message.date,
        username=update.effective_user.username,
        full_name=update.effective_user.full_name,
    )
