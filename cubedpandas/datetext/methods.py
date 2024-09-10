from datetime import datetime
from dateutil.parser import parse as dateutil_parse, parserinfo
from dateutil.relativedelta import MO
from dateutil.parser import ParserError
from dateutil.relativedelta import relativedelta
from pyspark.sql.functions import last_day


# DateText Methods to resolve date- and time-related text
# shared methods to be used by all languages

# region helper methods
def shift(tuple: (datetime, datetime), years: int = 0, months: int = 0, days: int = 0, weeks: int = 0,
          hours: int = 0, minutes: int = 0, seconds: int = 0, microseconds: int = 0) -> (datetime, datetime):
    """Shifts a date tuple by the given delta."""
    return tuple[0] + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes,
                                    seconds=seconds, microseconds=microseconds, weeks=weeks), \
           tuple[1] + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes,
                                    seconds=seconds, microseconds=microseconds)


# region Single Token DateText Methods
def now():
    return datetime.now()


def tomorrow(offset_days: int = 0):
    dtv = datetime.now() + relativedelta(days=offset_days + 1)
    return (dtv.replace(hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(hour=23, minute=59, second=59, microsecond=999999))


def today(offset_days: int = 0):
    dtv = datetime.now() + relativedelta(days=offset_days)
    return (dtv.replace(hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(hour=23, minute=59, second=59, microsecond=999999))


def yesterday(offset_days: int = 0):
    dtv = datetime.now() + relativedelta(days=offset_days - 1)
    return (dtv.replace(hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(hour=23, minute=59, second=59, microsecond=999999))


def ytd(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # year to date
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(hour=23, minute=59, second=59, microsecond=999999))


def mtd(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # month to date
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(hour=23, minute=59, second=59, microsecond=999999))


def qtd(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # quarter to date
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=(dtv.month - 1) % 3 + 1, day=1, hour=23, minute=59, second=59, microsecond=999999))


def wtd(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # week to date - Monday is 0 and Sunday is 6
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(day=dtv.day - dtv.weekday(), hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(day=dtv.day - dtv.weekday() + 6, hour=23, minute=59, second=59, microsecond=999999))


def month(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # actual month from first to last day
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    last_day = dtv + relativedelta(day=31)
    return (dtv.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            last_day.replace(hour=23, minute=59, second=59, microsecond=999999))


def week(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # actual week from Monday to Sunday
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(day=dtv.day - dtv.weekday(), hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(day=dtv.day - dtv.weekday() + 6, hour=23, minute=59, second=59, microsecond=999999))


def quarter(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # actual quarter from first to last day
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    current_quarter = int((dtv.month - 1) / 3 + 1)
    first_day = datetime(dtv.year, 3 * current_quarter - 2, 1)
    last_day = first_day + relativedelta(months=3, days=-1)
    return (first_day.replace(hour=0, minute=0, second=0, microsecond=0),
            last_day.replace(hour=23, minute=59, second=59, microsecond=999999))


def year(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # actual year from first to last day
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999))


# endregion

# region Months and Days
def monday(offset_weeks: int = 0, offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # Monday is 0 and Sunday is 6
    dtv = datetime.now() + relativedelta(weekday=MO(-1), years=offset_years, months=offset_months, days=offset_days,
                                         weeks=offset_weeks)
    return (dtv.replace(hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(hour=23, minute=59, second=59, microsecond=999999))


def tuesday(offset_weeks: int = 0, offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # Tuesday is 1 and Sunday is 6
    return shift(monday(offset_weeks, offset_years, offset_months, offset_days), days=1)


def wednesday(offset_weeks: int = 0, offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # Wednesday is 2 and Sunday is 6
    return shift(monday(offset_weeks, offset_years, offset_months, offset_days), days=2)


def thursday(offset_weeks: int = 0, offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # Thursday is 3 and Sunday is 6
    return shift(monday(offset_weeks, offset_years, offset_months, offset_days), days=3)


def friday(offset_weeks: int = 0, offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # Friday is 4 and Sunday is 6
    return shift(monday(offset_weeks, offset_years, offset_months, offset_days), days=4)


def saturday(offset_weeks: int = 0, offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # Saturday is 5 and Sunday is 6
    return shift(monday(offset_weeks, offset_years, offset_months, offset_days), days=5)


def sunday(offset_weeks: int = 0, offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # Sunday is 6 and Sunday is 6
    return shift(monday(offset_weeks, offset_years, offset_months, offset_days), days=6)


def january(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=1, day=31, hour=23, minute=59, second=59, microsecond=999999))


def february(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    first_day = dtv.replace(month=2, day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = first_day + relativedelta(day=31)
    return (first_day,
            last_day.replace(hour=23, minute=59, second=59, microsecond=999999))


def march(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=3, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=3, day=31, hour=23, minute=59, second=59, microsecond=999999))


def april(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=4, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=4, day=30, hour=23, minute=59, second=59, microsecond=999999))


def may(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=5, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=5, day=31, hour=23, minute=59, second=59, microsecond=999999))


def june(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=6, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=6, day=30, hour=23, minute=59, second=59, microsecond=999999))


def july(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=7, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=7, day=31, hour=23, minute=59, second=59, microsecond=999999))


def august(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=8, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=8, day=31, hour=23, minute=59, second=59, microsecond=999999))


def september(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=9, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=9, day=30, hour=23, minute=59, second=59, microsecond=999999))


def october(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=10, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=10, day=31, hour=23, minute=59, second=59, microsecond=999999))


def november(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=11, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=11, day=30, hour=23, minute=59, second=59, microsecond=999999))


def december(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    dtv = datetime.now() + relativedelta(years=offset_years, months=offset_months, days=offset_days)
    return (dtv.replace(month=12, day=1, hour=0, minute=0, second=0, microsecond=0),
            dtv.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999))
# endregion
