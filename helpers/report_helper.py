import os
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from utils.storage import (
    get_group_total,
    get_group_pyhat,
    get_group_holittomat,
)


def get_report_timezone() -> timezone:
    try:
        return ZoneInfo(os.getenv("REPORT_TIMEZONE"))
    except ZoneInfoNotFoundError:
        print("REPORT_TIMEZONE not found, falling back to UTC.")
        return timezone.utc


REPORT_TIMEZONE = get_report_timezone()


def get_report_time(hour: int = 9, minute: int = 0) -> time:
    return time(hour=hour, minute=minute, tzinfo=REPORT_TIMEZONE)


def get_previous_year_month(now: datetime) -> str:
    previous_month = now.replace(day=1) - timedelta(days=1)
    return previous_month.strftime("%Y-%m")


def build_groupcount_text(chat_id: str) -> str:
    total = get_group_total(chat_id)
    pyha_total = get_group_pyhat(chat_id)
    holiton_total = get_group_holittomat(chat_id)
    return (
        f"Ryhmässä juotu yhteensä {total} kaliaa, "
        f"joista pyhiä {pyha_total}. "
        f"Ryhmässä juotu hoploppi juomia {holiton_total} kpl."
    )
