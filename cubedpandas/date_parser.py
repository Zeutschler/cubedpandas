# dates.py
# CubedPandas - Multi-dimensional data analysis for Pandas dataframes.
# ©2024 by Thomas Zeutschler. All rights reserved.
# MIT License - please see the LICENSE file that should have been included in this package.

from datetime import datetime, timedelta
import calendar
from dateutil.parser import parse
from typing import Any


def parse_date(value: Any) -> (datetime | None, datetime | None):
    """
    Tries to parse datetime information from a given value.

    If the value is a specific date, it will return a tuple of a datetime and None.
    If the value is a date range, it will return a tuple of first and last datetime in the range
    if the value is not a date, it will return a tuple (None, None).

    :param value: The datetime value to parse
    :return: a tuple of datetime objects
    """
    try:
        # Already a datetime object?
        if isinstance(value, datetime):
            return value, None
        if isinstance(value, timedelta):
            return datetime.now(), datetime.now() + value

        # Check for intervals gives as tuples or lists
        if isinstance(value, (tuple, list)):
            if len(value) >= 2:
                return parse_date(value[0])[0], parse_date(value[1])[0]

        # Check for intervals is defined by a dictionary
        if isinstance(value, dict):
            if "from" in value and "to" in value:
                return parse_date(value["from"])[0], parse_date(value["to"])[0]
            if "from" in value:
                return parse_date(value["from"])[0], datetime.max
            if "to" in value:
                return datetime.min, parse_date(value["to"])[0]

        if not isinstance(value, (str, int, float)):
            return None, None

        # Integers and floats can be timestamps or years
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        if isinstance(value, int):
            if value < 0:
                return None, None
            if datetime.min.year <= value <= datetime.max.year:
                return datetime(year=value, month=1, day=1), datetime(year=value, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            if datetime.min.timestamp() <= value <= datetime.max.timestamp():
                return datetime.fromtimestamp(value), None
        if isinstance(value, float):
            if datetime.min.timestamp() <= value <= datetime.max.timestamp():
                return datetime.fromtimestamp(value), None

        # Try to parse a date string
        try:
            dt = parse(value)

            # Check if the date has been guessed by dateutil.parser
            y_pos = value.find(str(dt.year))
            m_pos = value.find(str(dt.month))
            d_pos = value.find(str(dt.day))

            d_now = datetime.now().day

            if d_now == dt.day and (y_pos == -1 or m_pos == -1 or d_pos == -1):
                # Seems to be a guessed date.
                # Do not trust this.
                weekday, last = calendar.monthrange(dt.year, dt.month)
                return datetime(year=dt.year, month=dt.month, day=1), datetime(year=dt.year, month=dt.month, day=last, hour=23, minute=59, second=59, microsecond=999999)

            return dt, None
        except Exception as e:
            return None, None

    except Exception as e:
        # It's not a date...
        return None, None

