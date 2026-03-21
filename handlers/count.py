from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import load_counts

async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    counts = load_counts()

    if counts[user_id] <= 10:
        await update.message.reply_text(
            f'Kaliaa juotu {counts[user_id]} kpl. Avaappa se kalia jo..'
        )
    elif counts[user_id] <= 50:
        await update.message.reply_text(
            f'Kaliaa juotu {counts[user_id]} kpl. Muutama kalia mahtuis vielä.'
        )
    elif counts[user_id] <= 125:
        await update.message.reply_text(
            f'Kaliaa juotu {counts[user_id]} kpl. Aaa että.'
        )
    elif counts[user_id] <= 250:
        await update.message.reply_text(
            f'Kaliaa juotu {counts[user_id]} kpl. Kovaa kyytiä'
        )
    elif counts[user_id] > 250:
        await update.message.reply_text(
            f'Kaliaa juotu {counts[user_id]} kpl. Kaliaherra on ylpeä!'
        )