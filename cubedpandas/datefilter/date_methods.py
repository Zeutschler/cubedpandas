from datetime import datetime
from dateutil.parser import parse as dateutil_parse, parserinfo
from dateutil.relativedelta import MO
from dateutil.parser import ParserError
from dateutil.relativedelta import relativedelta
import pandas as pd
from pyspark.sql.functions import month

from cubedpandas.datefilter.date_span import DateSpan


# DateText Methods to resolve date- and time-related text
# shared methods to be used by all languages

# region helper methods

def df_filter_year(df: pd.DataFrame, column: str, year: int):
    index = df.iloc[df[column].dt.year == year].index.tonumpy()
    return index


# region Single Token DateText Methods
def now():
    return datetime.now()


def today(offset_days: int = 0) -> DateSpan:
    return DateSpan.now().full_day().shift(days=offset_days)


def tomorrow(offset_days: int = 0) -> DateSpan:
    return today(offset_days + 1)


def yesterday(offset_days: int = 0) -> DateSpan:
    return today(offset_days - 1)


def actual_ytd(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().ytd().shift(years=offset_years, months=offset_months, days=offset_days)


def actual_mtd(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().mtd().shift(years=offset_years, months=offset_months, days=offset_days)


def actual_qtd(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().qtd().shift(years=offset_years, months=offset_months, days=offset_days)


def actual_wtd(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().wtd().shift(years=offset_years, months=offset_months, days=offset_days)


def actual_month(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().full_month()


def actual_week(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().full_week()


def actual_quarter(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().full_quarter()


def actual_year(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().full_year()


# endregion

# region Months and Days
def monday(offset_weeks: int = 0, offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    # Monday is 0 and Sunday is 6
    dtv = datetime.now() + relativedelta(weekday=MO(-1), years=offset_years,
                                         months=offset_months, days=offset_days, weeks=offset_weeks)
    return DateSpan(dtv).full_day()


def tuesday():
    # Tuesday is 1 and Sunday is 6
    return monday().shift(days=1)


def wednesday():
    return monday().shift(days=2)


def thursday():
    return monday().shift(days=3)


def friday():
    return monday().shift(days=4)


def saturday():
    return monday().shift(days=5)


def sunday():
    return monday().shift(days=6)


def january(offset_years: int = 0, offset_months: int = 0, offset_days: int = 0):
    return DateSpan.now().replace(month=1).full_month()


def february():
    return DateSpan.now().replace(month=2).full_month()


def march():
    return DateSpan.now().replace(month=3).full_month()


def april():
    return DateSpan.now().replace(month=4).full_month()


def may():
    return DateSpan.now().replace(month=5).full_month()


def june():
    return DateSpan.now().replace(month=6).full_month()


def july():
    return DateSpan.now().replace(month=7).full_month()


def august():
    return DateSpan.now().replace(month=8).full_month()


def september():
    return DateSpan.now().replace(month=9).full_month()


def october():
    return DateSpan.now().replace(month=10).full_month()


def november():
    return DateSpan.now().replace(month=11).full_month()


def december():
    return DateSpan.now().replace(month=12).full_month()
# endregion
