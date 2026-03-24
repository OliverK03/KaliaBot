from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import get_count

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    count = get_count(chat_id, user_id)

    if count <= 10:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl. Avaappa se kalia jo..')
    elif count <= 50:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl. Muutama kalia mahtuis vielä.')
    elif count <= 125:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl. Aaa että.')
    elif count <= 250:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl. Kovaa kyytiä')
    else:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl. Kaliaherra on ylpeä!')