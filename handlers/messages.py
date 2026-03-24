from telegram import Update
from telegram.ext import ContextTypes
from typing import Optional


# Response Handler
async def handle_response(text: str) -> Optional[str]:
    processed: str = text.lower()
    rules = [
        ({"kalja"}, "opettele kirjottaa"),
        ({"hoplop"}, "ei oo mikään vitun hoploppi"),
    ]
    for triggers, reply in rules:
        if any(trigger in processed for trigger in triggers):
            return reply

    return None

# Gives info to console
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    response: Optional[str] = await handle_response(text)
    if not response:
        return

    print('Bot:', response)
    await update.message.reply_text(response)