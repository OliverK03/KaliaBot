from telegram import Update
from telegram.ext import ContextTypes
from handlers.counter import kalia_command
from handlers.count import count_command

async def handle_text_or_caption_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    content = (update.message.text or update.message.caption or "").strip()
    if not content:
        return
    
    command = content.split(maxsplit=1)[0].lower()
    command = command.split("@", maxsplit=1)[0]

    if command == "/kalia":
        await kalia_command(update, context)
    elif command == "/kaliacount":
        await count_command(update, context)