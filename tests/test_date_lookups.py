# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

import pandas as pd
from datetime import datetime, timedelta
from unittest import TestCase
from cubedpandas import cubed
from cubedpandas.context.datetime_resolver import parse_standard_date_token as parse


class TestDateLookUps(TestCase):
    """
    Note: Tests for the slice method only need be callable and error free.
    """

    def setUp(self) -> None:
        self._debug: bool = False
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        hour = datetime.now().hour
        minute = datetime.now().minute
        second = datetime.now().second

        data = {
            "product": ["A", "B", "C", "A", "B", "C"],
            "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
            "date": [datetime(year, month, day), datetime(year + 1, month, day), datetime(year - 1, month, day),
                     datetime(year, month, day) - timedelta(days=365), datetime(year, month, day) + timedelta(days=365),
                     datetime(year, month, day) - timedelta(days=31)],
            "sales": [100, 150, 300, 200, 250, 350],
            "cost": [50, 100, 200, 100, 150, 150]
        }
        self.df = pd.DataFrame.from_dict(data)

    def test_standard_dateTime_tokens(self):
        c = cubed(self.df)
        result, from_date, to_date = parse("today")

        a = c.date["today"]
        b = c.date[from_date:to_date]
        self.assertEqual(a, b)

        a = c.date.today
        b = c.date[from_date:to_date]
        self.assertEqual(a, b)

        result, from_date, to_date = parse("last year")
        a = c.date.last_year
        b = c.date[from_date:to_date]
        self.assertEqual(a, b)

    def test_all_stanard_dateTime_tokens(self):
        c = cubed(self.df)

        tokens = ["this minute", "last minute", "previous minute", "next minute", "this hour", "last hour",
                  "previous hour", "next hour",
                  "today", "yesterday", "tomorrow", "this year", "last year", "previous year", "next year",
                  "this month", "last month", "previous month", "next month",
                  "this week", "last week", "previous week", "next week", "this quarter", "last quarter",
                  "previous quarter", "next quarter", "this semester", "last semester",
                  "previous semester", "next semester"]

        for token in tokens:
            result, from_date, to_date = parse(token)
            a = c.date[token]
            b = c.date[from_date:to_date]
            self.assertEqual(a, b)
