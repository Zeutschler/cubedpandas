# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from datetime import datetime, timedelta
import calendar
from dateutil.parser import parse, ParserError
from typing import Any


def resolve_datetime(value: Any) -> (datetime | None, datetime | None):
    """
    A simple resolver for datetime information, e.g. `June`, `2024`, `2024-06`, `2024-06-01`,
    `2024-06-01 12:00:00` but also this year, last year, next year, yesterday, tomorrow, etc.
    String values will be parsed using dateutil.parser.parse method.

    If the value represents a specific date, it will return a tuple of a datetime and None.
    If the value represents a date range, it will return a tuple of first and last datetime in the range
    if the value does not represent a date, it will return a tuple (None, None).

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
                return resolve_datetime(value[0])[0], resolve_datetime(value[1])[0]

        # Check for intervals is defined by a dictionary
        if isinstance(value, dict):
            if "from" in value and "to" in value:
                return resolve_datetime(value["from"])[0], resolve_datetime(value["to"])[0]
            if "from" in value:
                return resolve_datetime(value["from"])[0], datetime.max
            if "to" in value:
                return datetime.min, resolve_datetime(value["to"])[0]

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
            year_pos = value.find(str(dt.year))
            month_num_pos = value.find(str(dt.month))
            day_num_pos = value.find(str(dt.day))

            d_now = datetime.now().day

            if d_now == dt.day and (year_pos == -1 or month_num_pos == -1 or day_num_pos == -1):
                # It seems to be a guessed date.
                # Do not trust this.
                weekday, last = calendar.monthrange(dt.year, dt.month)
                return datetime(year=dt.year, month=dt.month, day=1), datetime(year=dt.year, month=dt.month, day=last, hour=23, minute=59, second=59, microsecond=999999)

            # check for month names
            month_short_name_pos = str(value).lower().find(dt.strftime("%b").lower())
            month_long_name_pos = str(value).lower().find(dt.strftime("%B").lower())
            if month_short_name_pos > -1 or month_long_name_pos > -1:
                if day_num_pos == -1 or month_num_pos >= year_pos:
                    # no date given, just a month name and maybe a year
                    # get the first and last day of the month
                    weekday, last = calendar.monthrange(dt.year, dt.month)
                    return datetime(year=dt.year, month=dt.month, day=1), datetime(year=dt.year, month=dt.month,
                                                                                   day=last, hour=23, minute=59,
                                                                                   second=59, microsecond=999999)

            return dt, None

        except ParserError as e:
            # Failed to parse the date
            return None, None

    except Exception as e:
        # Whatever happened, it's not seem to be a date...
        return None, None

