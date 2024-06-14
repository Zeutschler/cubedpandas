import pandas as pd
from unittest import TestCase
from cubedpandas import Cube
from datetime import datetime

class TestCubeWithDates(TestCase):
    def setUp(self) -> None:
        data = {
            "product": ["A", "B", "C", "A", "B", "C"],
            "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
            "date": [datetime(2024, 6, 1), datetime(2024, 6, 2),
                     datetime(2024, 7, 1), datetime(2024, 7, 2),
                     datetime(2024, 12, 1), datetime(2023, 12, 2)],
            "sales": [100, 150, 300, 200, 250, 350]
        }
        self.df = pd.DataFrame.from_dict(data)
        self.schema = {
            "dimensions": [
                {"column": "product"},
                {"column": "channel"},
                {"column": "date"}
            ],
            "measures": [
                {"column": "sales"}
            ]
        }


    def test_simple_aggregations(self):

        cube = Cube(self.df, schema=self.schema)

        # simple aggregations
        value = cube["A"]
        self.assertEqual(value, 100 + 200)
        value = cube["B"]
        self.assertEqual(value, 150 + 250)
        value = cube["C"]
        self.assertEqual(value, 300 + 350)

        value = cube["Online"]
        self.assertEqual(value, 100 + 150 + 300)
        value = cube["Retail"]
        self.assertEqual(value, 200 + 250 + 350)

    def test_slicing_and_aggregations(self):
        cube = Cube(self.df, schema=self.schema)

        # slicing and aggregating
        value1 = cube["A", "Online"]
        self.assertEqual(value1, 100)
        value2 = cube["B", "Retail"]
        self.assertEqual(value2, 250)

        # arithmetic operation on slices
        total = value1 + value2
        self.assertEqual(total, 350)


    def test_slicing_with_exact_dates(self):
        cube = Cube(self.df, schema=self.schema)

        # slicing with dates
        some_date = datetime(2024, 6, 1)
        some_non_existing_date = datetime(2019, 3, 24)
        value = cube[some_date]
        self.assertEqual(value, 100)
        value = cube[some_non_existing_date]
        self.assertEqual(value, 0)

        value = cube["date:2024"]
        self.assertEqual(value, 100 + 150 + 300 + 200 + 250) # all sales in 2024, Note: last value is from 2023
