from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import get_count
from utils.storage import get_pyhat

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    count = get_count(chat_id, user_id)
    pyha_count = get_pyhat(chat_id, user_id)

    if count <= 10:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl, joista pyhiä {pyha_count} kpl. Avaappa se kalia jo..')
    elif count <= 50:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl, joista pyhiä {pyha_count} kpl. Muutama kalia mahtuis vielä.')
    elif count <= 125:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl, joista pyhiä {pyha_count} kpl. Aaa että.')
    elif count <= 250:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl, joista pyhiä {pyha_count} kpl. Kovaa kyytiä')
    else:
        await update.message.reply_text(f'Kaliaa juotu {count} kpl, joista pyhiä {pyha_count} kpl. Kaliaherra on ylpeä!')