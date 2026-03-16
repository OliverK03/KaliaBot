from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import load_counts, save_counts

async def counter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    counts = load_counts()

    counts[user_id] = counts.get(user_id, 0) + 1
    save_counts(counts)

    await update.message.reply_text(
        f'Kaliaa juotu {counts[user_id]} kpl.'
    )