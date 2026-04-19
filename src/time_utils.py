#!/usr/bin/env python3
"""
Timezone-aware date helpers for the application.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_timezone(timezone_name: str) -> ZoneInfo:
    """Return the configured timezone, falling back to UTC when unknown."""
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def get_now(timezone_name: str) -> datetime:
    """Return a timezone-aware current datetime."""
    return datetime.now(get_timezone(timezone_name))


def to_local_time(dt: datetime, timezone_name: str) -> datetime:
    """Convert a datetime to the configured timezone."""
    tz = get_timezone(timezone_name)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)
