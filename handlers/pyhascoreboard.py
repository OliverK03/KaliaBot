from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from utils.storage import get_pyhascoreboard


async def build_pyhascoreboard_text(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: str,
    rows: list[tuple[str, int]],
    title: str,
    empty_message: str,
) -> str:
    if not rows:
        return empty_message

    lines = [title]

    for index, (user_id, pyha_count) in enumerate(rows, start=1):
        display_name = f"Käyttäjä {user_id}"

        try:
            member = await context.bot.get_chat_member(
                chat_id=int(chat_id),
                user_id=int(user_id),
            )
            user = member.user
            display_name = f"@{user.username}" if user.username else user.full_name
        except (TelegramError, ValueError) as exc:
            print(f"Could not fetch scoreboard name for {user_id}: {exc}")

        prefix = ["🥇", "🥈", "🥉"][index - 1] if index <= 3 else f"{index}."
        lines.append(f"{prefix} {display_name} — {pyha_count}")

    return "\n".join(lines)


async def pyhascoreboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = str(update.effective_chat.id)
    rows = get_pyhascoreboard(chat_id)
    text = await build_pyhascoreboard_text(
        context,
        chat_id,
        rows,
        "Isoimmat Guinness-nautiskelijat",
        "Scoreboard on vielä tyhjä. Käytä /kalia ensin.",
    )
    await update.message.reply_text(text)
