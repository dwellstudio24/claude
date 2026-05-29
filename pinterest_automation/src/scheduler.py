from datetime import datetime, timedelta
from typing import Optional
import pytz

# Best Pinterest engagement windows (local time)
POSTING_TIMES = ["09:00", "13:30", "19:00"]


def build_schedule(
    count: int,
    start_offset_days: int = 1,
    spread_days: int = 14,
    timezone_str: str = "America/Los_Angeles",
) -> list:
    """
    Return list of UTC datetime objects for `count` pins,
    spread across `spread_days` starting `start_offset_days` from now.
    Pinterest requires publish_date between 1 min and 30 days from now.
    """
    tz = pytz.timezone(timezone_str)
    now = datetime.now(tz)
    start = (now + timedelta(days=start_offset_days)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    slots = []
    for day in range(spread_days):
        day_dt = start + timedelta(days=day)
        for time_str in POSTING_TIMES:
            h, m = map(int, time_str.split(":"))
            slot = day_dt.replace(hour=h, minute=m)
            if slot > now + timedelta(minutes=2):
                slots.append(slot)

    if not slots:
        raise ValueError("No valid scheduling slots found. Check spread_days and timezone.")

    if count <= len(slots):
        step = len(slots) / count
        selected = [slots[int(i * step)] for i in range(count)]
    else:
        selected = (slots * (count // len(slots) + 1))[:count]

    return [s.astimezone(pytz.utc) for s in selected]


def to_pinterest_format(dt: datetime) -> str:
    """ISO 8601 UTC string for Pinterest API."""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    utc = dt.astimezone(pytz.utc)
    return utc.strftime("%Y-%m-%dT%H:%M:%S")


def to_display_format(dt: datetime, timezone_str: str = "America/Los_Angeles") -> str:
    tz = pytz.timezone(timezone_str)
    local = dt.astimezone(tz)
    return local.strftime("%b %d, %Y @ %-I:%M%p %Z")
