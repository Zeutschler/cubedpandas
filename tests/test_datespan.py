from unittest import TestCase
from datetime import date, datetime, time, timedelta
from dateutil.parser import parse
from numpy.compat import asstr
from starlette.config import undefined

from cubedpandas.datefilter.date_span import DateSpan


class TestDateSpan(TestCase):
    def setUp(self):
        self.debug = self.is_debug()

    @staticmethod
    def is_debug():
        import sys
        gettrace = getattr(sys, 'gettrace', None)
        if gettrace is None:
            return False
        else:
            v = gettrace()
            if v is None:
                return False
            else:
                return True

    def test_initialization(self):
        dt1 = datetime(2024, 9, 9)
        dt2 = datetime(2024, 9, 10, 11, 12)

        ds = DateSpan(dt1, dt2)
        self.assertTrue(ds == (dt1, dt2))
        self.assertTrue(ds == DateSpan(dt1, dt2))

    def test_methods(self):
        dt1 = datetime(2024, 9, 9)
        dt2 = datetime(2024, 9, 10, 11, 12)

        undef = DateSpan.undefined()
        now = DateSpan.now()

        self.assertTrue(undef == (None, None))
        self.assertTrue(now.consecutive_with(DateSpan.now()))
        self.assertTrue(DateSpan.now().consecutive_with(now))

        self.assertTrue(DateSpan(dt1, dt2).consecutive_with(DateSpan(dt2, dt1)))
        self.assertTrue(DateSpan(dt1, dt2).overlaps_with(DateSpan(dt2, dt1)))

        jan = DateSpan.now().replace(month=1).full_month()
        feb = DateSpan.now().replace(month=2).full_month()
        mar = DateSpan.now().replace(month=3).full_month()

        # DateSpan arithmetic
        jan_feb = jan + feb
        jan_feb_mar = jan_feb + mar
        self.assertTrue(jan.start == jan_feb.start and jan_feb.end == feb.end)

        self.assertTrue(jan_feb_mar == jan + feb + mar)
        self.assertTrue(jan_feb_mar == jan.merge(feb).merge(mar))
        self.assertTrue(jan_feb_mar - jan == feb + mar)
        self.assertTrue(jan_feb_mar - (jan + feb + mar) == undef)

        self.assertTrue(mar > jan)
        self.assertTrue(jan < mar)
        self.assertFalse(jan > mar)
        self.assertFalse(jan > jan_feb_mar)

        with self.assertRaises(ValueError):
            result = jan_feb_mar - feb  # raises ValueError, as splitting would be required

        with self.assertRaises(ValueError):
            result = jan_feb_mar.subtract(feb)  # raises ValueError, as splitting would be required

        result = jan_feb_mar.subtract(feb, allow_split=True)
        self.assertTrue(isinstance(result, tuple))
        self.assertTrue(result[0] == jan and result[1] == mar)

        result = jan.merge(feb).merge(mar)
        self.assertTrue(result == jan_feb_mar)

        # date span overlap & consecutive
        self.assertFalse(jan.overlaps_with(feb))
        self.assertFalse(feb.overlaps_with(jan))
        self.assertFalse(jan.overlaps_with(mar))
        self.assertFalse(mar.overlaps_with(jan))
        self.assertTrue(jan.overlaps_with(jan))
        self.assertTrue(jan_feb.overlaps_with(jan))
        self.assertTrue(jan.overlaps_with(jan_feb))

        self.assertTrue(jan.consecutive_with(feb))
        self.assertTrue(feb.consecutive_with(jan))
        self.assertTrue(feb.consecutive_with(mar))
        self.assertFalse(jan.consecutive_with(mar))
        self.assertFalse(jan.consecutive_with(jan))

        # merge and intersect
        self.assertTrue(jan.merge(feb) == jan_feb)
        self.assertTrue(jan.intersect(feb) == undef)
        self.assertTrue(jan.intersect(jan_feb) == jan)
        self.assertTrue(jan.intersect(jan_feb_mar) == jan)
        self.assertTrue(jan.intersect(mar) == undef)

        # date span changes
        result = jan.with_time(time(12, 34, 56))
        to_be = DateSpan(jan.start.replace(hour=12, minute=34, second=56),
                         jan.end.replace(hour=12, minute=34, second=56, microsecond=0))
        self.assertTrue(result == to_be)

        self.assertEqual(now.full_second(),
                         DateSpan(now.start.replace(microsecond=0), now.end.replace(microsecond=999999)))
        self.assertEqual(now.full_minute(), DateSpan(now.start.replace(second=0, microsecond=0),
                                                     now.end.replace(second=59, microsecond=999999)))
        self.assertEqual(now.full_hour(), DateSpan(now.start.replace(minute=0, second=0, microsecond=0),
                                                   now.end.replace(minute=59, second=59, microsecond=999999)))
        self.assertEqual(now.full_day(), DateSpan(now.start.replace(hour=0, minute=0, second=0, microsecond=0),
                                                  now.end.replace(hour=23, minute=59, second=59, microsecond=999999)))
        result = now.full_week()  # to lazy to write a test, copilot to stupid
        result = now.full_month()  # to lazy to write a test, copilot to stupid
        result = now.full_quarter()  # to lazy to write a test, copilot to stupid
        self.assertEqual(now.full_year(),
                         DateSpan(now.start.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
                                  now.end.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)))

        # date span shifting
        self.assertTrue(jan.shift(months=1) == feb)
        self.assertTrue(jan.shift(months=2) == mar)
        self.assertTrue(mar.shift(months=-2) == jan)

        self.assertTrue(jan.shift(weeks=1) == DateSpan(jan.start + timedelta(days=7), jan.end + + timedelta(days=7)))
        self.assertTrue(jan.shift(days=1) == DateSpan(jan.start + timedelta(days=1), jan.end + + timedelta(days=1)))

        self.assertTrue(jan.shift_end(months=1) == jan_feb)
        self.assertTrue(jan_feb.shift_start(months=1) == feb)
        self.assertTrue(jan.shift_start(months=1) == undef)

        # other methods
        self.assertTrue(jan.to_tuple() == (jan.start, jan.end))
        self.assertTrue(jan.duration == (jan.end - jan.start).total_seconds() / 86400.0)
        self.assertTrue(jan.timedelta == jan.end - jan.start)

        self.assertTrue(jan.begins_on_month_start)
        self.assertTrue(jan.ends_on_month_end)
        self.assertTrue(jan.is_full_month)

        self.assertFalse(DateSpan.today().is_undefined)

        jan.start = jan.start.replace(year=2023)
        jan.end = jan.end.replace(year=2023)
        self.assertTrue(jan.is_full_month)

        self.assertTrue(jan.__hash__() == (jan.start, jan.end).__hash__())
