import re

from telegram import Update
from telegram.ext import ContextTypes

from handlers.count import count_command
from handlers.counter import kalia_command
from handlers.pyhacounter import pyha_command
from handlers.scoreboard import scoreboard_command


async def handle_text_or_caption_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    caption = (update.message.caption or "").strip()
    if not caption:
        return

    commands = {
        match.split("@", maxsplit=1)[0]
        for match in re.findall(r"/[\w@]+", caption.lower())
    }
    print("caption:", caption)
    print("commands:", commands)

    if "/kalia" in commands:
        await kalia_command(update, context)
    elif "/pyha" in commands:
        await pyha_command(update, context)
    elif "/kaliacount" in commands:
        await count_command(update, context)
    elif commands.intersection({"/scoreboard", "/kaliatop"}):
        await scoreboard_command(update, context)