from telegram.error import TelegramError
from telegram.ext import ContextTypes
from helpers.report_helper import build_groupcount_text

from utils.storage import get_all_chat_ids


async def send_daily_groupcount(context: ContextTypes.DEFAULT_TYPE):
    chat_ids = get_all_chat_ids()
    if not chat_ids:
        print("No chats registered for daily group count.")
        return

    for chat_id in chat_ids:
        message = build_groupcount_text(chat_id)
        try:
            await context.bot.send_message(chat_id=int(chat_id), text=message)
        except (TelegramError, ValueError) as exc:
            print(f"Could not send daily group count to chat {chat_id}: {exc}")

