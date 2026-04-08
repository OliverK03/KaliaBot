from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'/kalia - Lisää kalian laskuriin\n'
        f'/kaliacount - Oman kalialaskurin määrä\n'
        f'/groupcount - Ryhmän kaikki kaliat yhteensä\n'
        f'/kaliatop - Ryhmän top kaliajuojat (all-time)\n'
        f'Kuukausiraportti lähetetään automaattisesti kuun 1. päivä.'
    )