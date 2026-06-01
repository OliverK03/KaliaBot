from datetime import datetime
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from handlers.scoreboard import build_scoreboard_text, scoreboard_command

from helpers.report_helper import REPORT_TIMEZONE, get_previous_year_month
from utils.storage import (
    get_all_chat_ids,
    get_monthly_group_total,
    get_monthly_group_pyha_total,
    get_monthly_pyhascoreboard,
    get_monthly_scoreboard,
    has_monthly_report_been_sent,
    mark_monthly_report_sent,
)


async def send_monthly_kalia_report(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(REPORT_TIMEZONE)
    if now.day != 1:
        print(f"[monthly report] skipping, not day 1")
        return

    year_month = get_previous_year_month(now)
    print(f"[monthly report] year_month={year_month}, chats={get_all_chat_ids()}")

    for chat_id in get_all_chat_ids():
        if has_monthly_report_been_sent(chat_id, year_month):
            continue

        rows = get_monthly_scoreboard(chat_id, year_month)
        pyha_rows = get_monthly_pyhascoreboard(chat_id, year_month)
        monthly_total = get_monthly_group_total(chat_id, year_month)
        monthly_pyhat = get_monthly_group_pyha_total(chat_id, year_month)
        # Peruskalia-scoreboard
        kalia_message = await build_scoreboard_text(
            context,
            chat_id,
            rows,
            f"🍺 Kalia kuukausiraportti ({year_month})\nYhteensä ryhmässä: {monthly_total} juotua kaliaa.",
            f"🍺 Kalia kuukausiraportti ({year_month})\nYhteensä ryhmässä: 0 juotua kaliaa.\nEi juotuja kalioja viime kuussa.",
        )
        print(f"[monthly report] fired at {now}, day={now.day}, tz={REPORT_TIMEZONE}")

        # Pyhä-kalia-scoreboard (perustuu pyha_countiin)
        pyha_message = await build_scoreboard_text(
            context,
            chat_id,
            pyha_rows,
            f"Guinnessejä juotu {monthly_pyhat}.",
            f"Viime kuussa ei ollut yhtään pyhää kaliaa.",
        )

        message = f"{kalia_message}\n\n{pyha_message}"

        try:
            await context.bot.send_message(chat_id=int(chat_id), text=message)
            mark_monthly_report_sent(chat_id, year_month)
        except (TelegramError, ValueError) as exc:
            print(f"Could not send monthly report to chat {chat_id}: {exc}")