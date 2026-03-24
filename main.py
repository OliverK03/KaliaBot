import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from config.settings import BOT_TOKEN
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from handlers.counter import kalia_command
from handlers.count import count_command
from handlers.groupcount import groupcount_command
from handlers.help import help_command
from handlers.messages import handle_message
from handlers.text_or_caption import handle_text_or_caption_command


# Healthserver jotta render deployaa web-service apin.
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/healthz"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        self.send_response(404)
        self.end_headers()
    
    def log_message(self, format, *args):
        return
    
def start_health_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(targer=server.serve_forever, deamon=True).start()
    print(f"Health server listerning on port {port}")

""" Commands, perjaatteessa kyl nä on turhat lol
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Kaliaaa!!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('lissää kaliaa')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
"""

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('kalia', kalia_command))
    app.add_handler(CommandHandler('kaliacount', count_command))
    app.add_handler(CommandHandler('groupcount', groupcount_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Caption
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_text_or_caption_command))

    # Errors
    app.add_error_handler(error)

    start_health_server()
    print('Polling...')
    app.run_polling(poll_interval=3)