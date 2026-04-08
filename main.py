import os
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from config.settings import BOT_TOKEN
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from handlers.count import count_command
from handlers.counter import kalia_command
from handlers.groupcount import groupcount_command
from handlers.help import help_command
from handlers.messages import handle_message
from handlers.scoreboard import build_scoreboard_text, scoreboard_command
from handlers.text_or_caption import handle_text_or_caption_command
from utils.storage import (
    get_all_chat_ids,
    get_monthly_group_total,
    get_monthly_scoreboard,
    has_monthly_report_been_sent,
    mark_monthly_report_sent,
)


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
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Health server listerning on port {port}")


try:
    REPORT_TIMEZONE = ZoneInfo(os.getenv("REPORT_TIMEZONE", "Europe/Helsinki"))
except ZoneInfoNotFoundError:
    REPORT_TIMEZONE = timezone.utc
    print("REPORT_TIMEZONE not found, falling back to UTC.")


def _get_previous_year_month(now: datetime) -> str:
    previous_month = now.replace(day=1) - timedelta(days=1)
    return previous_month.strftime("%Y-%m")


async def send_monthly_kalia_report(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(REPORT_TIMEZONE)
    if now.day != 1:
        return

    year_month = _get_previous_year_month(now)

    for chat_id in get_all_chat_ids():
        if has_monthly_report_been_sent(chat_id, year_month):
            continue

        rows = get_monthly_scoreboard(chat_id, year_month)
        monthly_total = get_monthly_group_total(chat_id, year_month)
        message = await build_scoreboard_text(
            context,
            chat_id,
            rows,
            f"🍺 Kalia kuukausiraportti ({year_month})\nYhteensä ryhmässä: {monthly_total} juotua kaliaa.",
            f"🍺 Kalia kuukausiraportti ({year_month})\nYhteensä ryhmässä: 0 juotua kaliaa.\nEi juotuja kalioja viime kuussa.",
        )

        try:
            await context.bot.send_message(chat_id=int(chat_id), text=message)
            mark_monthly_report_sent(chat_id, year_month)
        except (TelegramError, ValueError) as exc:
            print(f"Could not send monthly report to chat {chat_id}: {exc}")

""" Commands, perjaatteessa kyl nä on turhat lol
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Kaliaaa!!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('lissää kaliaa')
"""
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('kaliacount', count_command))
    app.add_handler(CommandHandler('groupcount', groupcount_command))
    app.add_handler(CommandHandler(['scoreboard', 'kaliatop'], scoreboard_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Caption
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_text_or_caption_command))

    # Errors
    app.add_error_handler(error)

    if app.job_queue:
        app.job_queue.run_repeating(
            send_monthly_kalia_report,
            interval=3600,
            first=10,
            name='monthly_kalia_report',
        )
    start_health_server()
    print('Polling...')
    app.run_polling(poll_interval=3)