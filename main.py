import os
from config.settings import BOT_TOKEN, BOT_USERNAME
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from handlers.counter import kalia_command
from handlers.count import count_command
from handlers.help import help_command
from handlers.messages import handle_message
from handlers.text_or_caption import handle_text_or_caption_command

#Commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Kaliaaa!!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('lissää kaliaa')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('kalia', kalia_command))
    app.add_handler(CommandHandler('kaliacount', count_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Caption
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_text_or_caption_command))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)