from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f'/kalia - Lisää kalian laskuriin\n'
        f'/kaliacount - Oman kalialaskurin määrä\n'
        f'/pyha - Lisää yhden Guinnessin laskuriin\n'
        f'/hoplop - Holittomien kaliojen counter\n'
        f'/groupcount - Ryhmän kaikki kaliat yhteensä\n'
        f'/kaliatop - Ryhmän top kaliajuojat \n'
        f'/pyhatop - Ryhmän top Guinnessin juojat\n'
        f'Kuukausiraportti lähetetään automaattisesti kuun 1. päivä.'
    )