from __future__ import annotations
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta


class DateSpan:
    """
    Represents a time span with a start and end date. The DateSpan can be used to compare, merge, intersect, subtract
    and shift date spans. The DateSpan can be used to represent a full day, week, month, quarter or year.

    The DateSpan is immutable, all methods that change the DateSpan will return a new DateSpan.
    """
    TIME_EPSILON_MICROSECONDS = 1000  # 1 millisecond

    def __init__(self, start: datetime | None, end: datetime | None = None):
        self._start: datetime | None = start
        self._end: datetime | None = end if end is not None else start

    @classmethod
    def now(cls) -> DateSpan:
        """Returns a new DateSpan with the start and end date set to the current date and time."""
        now = datetime.now()
        return DateSpan(now, now)

    @classmethod
    def today(cls) -> DateSpan:
        """Returns a new DateSpan with the start and end date set to the current date."""
        return DateSpan.now().full_day()

    @classmethod
    def undefined(cls) -> DateSpan:
        """Returns an empty / undefined DateSpan."""
        return DateSpan(None, None)

    @property
    def is_undefined(self) -> bool:
        """Returns True if the DateSpan is undefined."""
        return self._start is None and self._end is None

    @property
    def start(self) -> datetime:
        """Returns the start date of the DateSpan."""
        return self._start

    @start.setter
    def start(self, value: datetime):
        self._start = value
        self._swap()

    @property
    def end(self) -> datetime:
        """Returns the end date of the DateSpan."""
        return self._end

    @end.setter
    def end(self, value: datetime):
        self._end = value
        self._swap()

    def __getitem__(self, item):
        if item == 0:
            return self._start
        if item == 1:
            return self._end
        raise IndexError("Index out of range. DateSpan only supports index 0 and 1.")

    def clone(self) -> DateSpan:
        """Returns a new DateSpan with the same start and end date."""
        return DateSpan(self._start, self._end)

    def overlaps_with(self, other: DateSpan) -> bool:
        """
        Returns True if the DateSpan overlaps with the given DateSpan.
        """
        if self.is_undefined or other.is_undefined:
            return False
        if self._start >= other._start:
            return self._start <= other._end
        return self._end >= other._start

    def consecutive_with(self, other: DateSpan) -> bool:
        """
        Returns True if the DateSpan is consecutive to the given DateSpan, the follow each other without overlap.
        """
        if self.is_undefined or other.is_undefined:
            return False
        if self._start > other._start:
            delta = self._start - other._end
            return timedelta(microseconds=0) <= delta <= timedelta(microseconds=self.TIME_EPSILON_MICROSECONDS)
        delta = other._start - self._end
        return timedelta(microseconds=0) <= delta <= timedelta(microseconds=self.TIME_EPSILON_MICROSECONDS)

    def merge(self, other: DateSpan) -> DateSpan:
        """
        Returns a new DateSpan that is the merge of the DateSpan with the given DateSpan. Merging is only
        possible if the DateSpan overlap or are consecutive.
        """
        if self.is_undefined:
            return other
        if other.is_undefined:
            return self
        if self.overlaps_with(other) or self.consecutive_with(other):
            return DateSpan(min(self._start, other._start), max(self._end, other._end))
        raise ValueError("Cannot merge DateSpans that do not overlap or are not consecutive.")

    def intersect(self, other: DateSpan) -> DateSpan:
        """
        Returns a new DateSpan that is the intersection of the DateSpan with the given DateSpan.
        If there is no intersection, an undefined DateSpan is returned.
        """
        if self.is_undefined:
            return other
        if other.is_undefined:
            return self
        if self.overlaps_with(other):
            return DateSpan(max(self._start, other._start), min(self._end, other._end))
        return DateSpan.undefined()

    def subtract(self, other: DateSpan, allow_split: bool = False) -> DateSpan | (DateSpan, DateSpan):
        """
        Returns a new DateSpan that is the subtraction of the DateSpan with the given DateSpan.
        If there is no overlap, the DateSpan will be returned unchanged.
        If the other DateSpan is fully overlapped by the DateSpan, depending on the `allow_split` argument,
        the DateSpan will be split into two DateSpans or an ValueError will be raised, indicating that the
        subtraction can not yield a single DateSpan.

        Arguments:
            allow_split: If True, the DateSpan will be split into two DateSpans if the given
                DateSpan is overlapping. In that case, a tuple of two DateSpans will be returned.
        """
        if self.is_undefined:
            return DateSpan.undefined()
        if other.is_undefined:
            return self
        if other in self:
            # the other is fully overlapped by self
            if self in other:
                # both spans are identical, subtraction will result in an undefined/empty DateSpan
                return DateSpan.undefined()
            if other._start == self._start:  # special case: same start for both spans, cut out the other span
                # we need to full cut out the other span, so we need to go 1 microsecond behind its end
                return DateSpan(other._end + timedelta(microseconds=1), self._end)
            if other._end == self._end:  # special case: same end for both spans, cut out the other span
                # we need to full cut out the other span, so we need to go 1 microsecond before its start
                return DateSpan(self._start, other._start - timedelta(microseconds=1))
            if allow_split:
                return (
                    DateSpan(self._start, other._start - timedelta(microseconds=1)),
                    DateSpan(other._end + timedelta(microseconds=1), self._end)
                )
            raise ValueError("Cannot subtract DateSpan that fully overlaps, without splitting.")

        if not self.overlaps_with(other):
            # no overlapping at all, return self
            return self.clone()

        if other._start < self._start:
            # overalap at the start
            return DateSpan(other._end + timedelta(microseconds=1), self._end)
        # overlap at the end
        return DateSpan(self._start, other._start - timedelta(microseconds=1))

    def with_time(self, time: datetime | time) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the given date and time.
        """
        start = self._start.replace(hour=time.hour, minute=time.minute, second=time.second,
                                    microsecond=time.microsecond)
        end = self._end.replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=time.microsecond)
        return DateSpan(start, end)

    def full_second(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the respective second(s).
        """
        return DateSpan(self._start.replace(microsecond=0),
                        self._end.replace(microsecond=999999))

    def full_minute(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the respective minute(s).
        """
        return DateSpan(self._start.replace(second=0, microsecond=0),
                        self._end.replace(second=59, microsecond=999999))

    def full_hour(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the respective hour(s).
        """
        return DateSpan(self._start.replace(minute=0, second=0, microsecond=0),
                        self._end.replace(minute=59, second=59, microsecond=999999))

    def full_day(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the respective day(s).
        """
        return DateSpan(self._start.replace(hour=0, minute=0, second=0, microsecond=0),
                        self._end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def full_week(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the respective week(s).
        """
        start = self._start - relativedelta(days=self._start.weekday())
        end = self._end + relativedelta(days=6 - self._end.weekday())
        return DateSpan(start.replace(hour=0, minute=0, second=0, microsecond=0),
                        end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def full_month(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the respective month(s).
        """
        start = self._start.replace(day=1)
        end = self._end.replace(day=1) + relativedelta(day=31)
        return DateSpan(start.replace(hour=0, minute=0, second=0, microsecond=0),
                        end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def full_quarter(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the respective quarter(s).
        """
        start = self._start.replace(month=(self._start.month // 3) * 3, day=1, hour=0, minute=0, second=0,
                                    microsecond=0)
        end = self._end.replace(month=(self._end.month // 3) * 3 + 1, day=1, hour=23, minute=59, second=59,
                                microsecond=999999) + relativedelta(months=3, days=-1)
        return DateSpan(start.replace(hour=0, minute=0, second=0, microsecond=0),
                        end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def full_year(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the respective year(s).
        """
        start = self._start.replace(month=1, day=1)
        end = self._end.replace(month=1, day=1) + relativedelta(years=1, days=-1)
        return DateSpan(start.replace(hour=0, minute=0, second=0, microsecond=0),
                        end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def ytd(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the year-to-date.
        """
        start = self._start.replace(month=1, day=1)
        end = self._start
        return DateSpan(start.replace(hour=0, minute=0, second=0, microsecond=0),
                        end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def mtd(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the month-to-date.
        """
        start = self._start.replace(day=1)
        end = self._start
        return DateSpan(start.replace(hour=0, minute=0, second=0, microsecond=0),
                        end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def qtd(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the quarter-to-date.
        """
        start = self._start.replace(month=(self._start.month // 3) * 3 + 1, day=1)
        end = self._start
        return DateSpan(start.replace(hour=0, minute=0, second=0, microsecond=0),
                        end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def wtd(self) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date set to the beginning and end of the week-to-date.
        """
        start = self._start - relativedelta(days=self._start.weekday())
        end = self._start
        return DateSpan(start.replace(hour=0, minute=0, second=0, microsecond=0),
                        end.replace(hour=23, minute=59, second=59, microsecond=999999))

    def _begin_of_day(self, dt: datetime) -> datetime:
        """Returns the beginning of the day for the given datetime."""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def _end_of_day(self, dt: datetime) -> datetime:
        """Returns the end of the day for the given datetime."""
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    def _begin_of_month(self, dt: datetime) -> datetime:
        """Returns the beginning of the month for the given datetime."""
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _end_of_month(self, dt: datetime) -> datetime:
        """Returns the end of the month for the given datetime."""
        return dt.replace(day=1, hour=23, minute=59, second=59, microsecond=999999) + relativedelta(months=1, days=-1)

    def _last_day_of_month(self, dt: datetime) -> datetime:
        # The day 28 exists in every month. 4 days later, it's always next month
        next_month = dt.replace(day=28) + timedelta(days=4)
        # subtracting the number of the current day brings us back one month
        last_day = next_month - timedelta(days=next_month.day)
        last_day.replace(hour=23, minute=59, second=59, microsecond=999999)
        return last_day

    def _first_day_of_month(self, dt: datetime) -> datetime:
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @property
    def ends_on_month_end(self) -> bool:
        """
        Returns True if the DateSpan ends on the last day of the month.
        """
        return self._end == self._last_day_of_month(self._end)

    @property
    def begins_on_month_start(self) -> bool:
        """
        Returns True if the DateSpan begins on the first day of the month.
        """
        return self._start == self._first_day_of_month(self._start)

    @property
    def is_full_month(self) -> bool:
        """
        Returns True if the DateSpan is a full month.
        """
        return (self._start == self._begin_of_month(self._start) and
                self._end == self._end_of_month(self._end))

    def _swap(self) -> DateSpan:
        """Swap start and end date if start is greater than end."""
        if self._start > self._end:
            tmp = self._start
            self._start = self._end
            self._end = tmp
        return self

    def replace(self, year: int | None = None, month: int | None = None, day: int | None = None,
                hour: int | None = None,
                minute: int | None = None, second: int | None = None, microsecond: int | None = None) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date replaced by the given datetime parts.
        """
        if year is None:
            year = self._start.year
        if month is None:
            month = self._start.month
        if day is None:
            day = self._start.day
        if hour is None:
            hour = self._start.hour
        if minute is None:
            minute = self._start.minute
        if second is None:
            second = self._start.second
        if microsecond is None:
            microsecond = self._start.microsecond
        start = self._start.replace(year=year, month=month, day=day, hour=hour, minute=minute,
                                    second=second, microsecond=microsecond)

        if year is None:
            year = self._end.year
        if month is None:
            month = self._end.month
        if day is None:
            day = self._end.day
        if hour is None:
            hour = self._end.hour
        if minute is None:
            minute = self._end.minute
        if second is None:
            second = self._end.second
        if microsecond is None:
            microsecond = self._end.microsecond
        end = self._end.replace(year=year, month=month, day=day, hour=hour, minute=minute,
                                second=second, microsecond=microsecond)
        if self.ends_on_month_end:
            # months and years need to be shifted to proper month end
            end = self._end_of_month(end)

        return DateSpan(start, end)._swap()

    def shift(self, years: int = 0, months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0,
              microseconds: int = 0, weeks: int = 0) -> DateSpan:
        """
        Returns a new DateSpan with the start and end date shifted by the given +/- time delta.
        """
        if self.is_undefined:
            raise ValueError("Cannot shift undefined DateSpan.")
        start = self._start + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes,
                                            seconds=seconds, microseconds=microseconds)

        end = self._end + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes,
                                        seconds=seconds, microseconds=microseconds)
        if weeks:
            start += timedelta(weeks=weeks)
            end += timedelta(weeks=weeks)
        elif days or hours or minutes or seconds or microseconds:
            pass
        elif self.ends_on_month_end:
            # months and years need to be shifted to proper month end
            end = self._end_of_month(end)
        return DateSpan(start, end)

    def shift_start(self, years: int = 0, months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0,
                    seconds: int = 0,
                    microseconds: int = 0, weeks: int = 0):
        """
        Shifts the start date of the DateSpan by the given +/- time delta.
        """
        if self.is_undefined:
            raise ValueError("Cannot shift undefined DateSpan.")
        start = self._start + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes,
                                            seconds=seconds, microseconds=microseconds)
        if weeks:
            start += timedelta(weeks=weeks)
        result = DateSpan(start, self._end)._swap()
        if result.end - result.start < timedelta(microseconds=self.TIME_EPSILON_MICROSECONDS):
            return DateSpan.undefined()
        return result

    def shift_end(self, years: int = 0, months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0,
                  seconds: int = 0,
                  microseconds: int = 0, weeks: int = 0):
        """
        Shifts the end date of the DateSpan by the given +/- time delta.
        """
        if self.is_undefined:
            raise ValueError("Cannot shift undefined DateSpan.")
        end = self._end + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes,
                                        seconds=seconds, microseconds=microseconds)
        if weeks:
            end += timedelta(weeks=weeks)
        elif days or hours or minutes or seconds or microseconds:
            pass
        elif self.ends_on_month_end:
            # months and years need to be shifted to proper month end
            end = self._end_of_month(end)
        result = DateSpan(self._start, end)._swap()
        if result.end - result.start < timedelta(microseconds=self.TIME_EPSILON_MICROSECONDS):
            return DateSpan.undefined()
        return result

    @property
    def timedelta(self) -> timedelta:
        """
        Returns the time delta between the start and end date of the DateSpan. Same as `duration`.
        """
        return self._end - self._start

    @property
    def duration(self) -> float:
        """
        Returns the duration of the DateSpan in days as a float. Decimal digits represent fractions of a day.
        """
        return (self._end - self._start).total_seconds() / 86400.0

    def to_tuple(self) -> tuple[datetime, datetime]:
        """
        Returns the start and end date of the DateSpan as a tuple.
        """
        return self._start, self._end

    def __add__(self, other):
        if isinstance(other, timedelta):
            return DateSpan(self._start + other, self._end + other)
        if isinstance(other, DateSpan):
            return self.merge(other)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return DateSpan(self._start - other, self._end - other)
        if isinstance(other, DateSpan):
            return self.subtract(other)
        return NotImplemented

    def __contains__(self, item):
        if isinstance(item, datetime):
            return self._start <= item <= self._end
        if isinstance(item, DateSpan):
            return self._start <= item.start <= item.end <= self._end
        if isinstance(item, float):
            item = datetime.fromtimestamp(item)
            return self.start <= item <= self.end
        return False

    def __bool__(self):
        return not (self._start is None and self._end is None)

    def __str__(self):
        self.__repr__()

    def __repr__(self):
        if self.is_undefined:
            return "DateSpan(undefined)"
        return (f"DateSpan({self._start.strftime('%a %Y-%m-%d %H:%M:%S')} <-> "
                f"{self._end.strftime('%a %Y-%m-%d %H:%M:%S')})")

    def __eq__(self, other):
        if other is None:
            return self._start is None and self._end is None
        if isinstance(other, DateSpan):
            return self.start == other.start and self.end == other.end
        if isinstance(other, datetime):
            return self.start == other and self.end == other
        if isinstance(other, tuple):
            return self.start == other[0] and self.end == other[1]
        if isinstance(other, float):
            other = datetime.fromtimestamp(other)
            return self.start == other and self.end == other
        return False

    def __gt__(self, other):
        if isinstance(other, DateSpan):
            return self.start > other.start and self.end > other.end
        if isinstance(other, datetime):
            return self.start > other and self.end > other
        if isinstance(other, tuple):
            return self.start > other[0] and self.end > other[1]
        if isinstance(other, float):
            other = datetime.fromtimestamp(other)
            return self.start > other and self.end > other
        return False

    def __lt__(self, other):
        if isinstance(other, DateSpan):
            return self.start < other.start and self.end < other.end
        if isinstance(other, datetime):
            return self.start < other and self.end < other
        if isinstance(other, tuple):
            return self.start < other[0] and self.end < other[1]
        if isinstance(other, float):
            other = datetime.fromtimestamp(other)
            return self.start < other and self.end < other
        return False

    def __hash__(self):
        return hash((self._start, self._end))
