import dateparser
from datetime import datetime, timedelta


def parse_date(date_string:str) -> (datetime | None, datetime | None):
    """
    Tries to parse a datetime from a string.
    If the string is a specific date, it will return a tuple of a datetime and None.
    If the string is a date range, it will return a tuple of first and last datetime in the range

    :param date_string: The date string to parse
    :return: a tuple of datetime objects
    """
    try:
        # Try to parse a specific date
        parsed_date = dateparser.parse(date_string, settings={'STRICT_PARSING': True})
        if not (parsed_date is None):
            return parsed_date, None

        # No specific date? Let's try to parse a date range, e.g. from strings like "June 2024", "June" or "2024"
        parsed_first_date = dateparser.parse(
            date_string= date_string,
            settings={"STRICT_PARSING": False,
                      "PREFER_DAY_OF_MONTH": "first",
                      "PREFER_MONTH_OF_YEAR": "first",
                      "PREFER_DATES_FROM": "past"})
        parsed_last_date = dateparser.parse(
            date_string=date_string,
            settings={"STRICT_PARSING": False,
                      "PREFER_DAY_OF_MONTH": "last",
                      "PREFER_MONTH_OF_YEAR": "last",
                      "PREFER_DATES_FROM": "past"})
        if parsed_last_date.hour == 0 and parsed_last_date.minute == 0 and parsed_last_date.second == 0 and parsed_last_date.microsecond == 0:
            parsed_last_date += (timedelta(days=1) - timedelta(microseconds=1))

        return parsed_first_date, parsed_last_date
    except Exception as e:
        # It's not a date...
        return None, None

