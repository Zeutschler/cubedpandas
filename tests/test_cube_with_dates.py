import pandas as pd
from unittest import TestCase
from cubedpandas import Cube
from datetime import datetime

class TestCube(TestCase):
    def setUp(self) -> None:
        data = {
            "product": ["A", "B", "C", "A", "B", "C"],
            "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
            "date": [datetime(2024, 6, 1), datetime(2024, 6, 2),
                     datetime(2024, 7, 1), datetime(2024, 7, 2),
                     datetime(2024, 12, 1), datetime(2024, 12, 2)],
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

    def test_cube_with_dates(self):

        cube = Cube(self.df, schema=self.schema)

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

        value = cube["A", "Online"]
        self.assertEqual(value, 100)
        value = cube["B", "Retail"]
        self.assertEqual(value, 250)

        some_date = datetime(2024, 6, 1)
        some_non_existing_date = datetime(2019, 3, 24)
        value = cube[some_date]
        self.assertEqual(value, 100)
        value = cube[some_non_existing_date]
        self.assertEqual(value, 0)


    def test_slice(self):

        cube = Cube(self.df, schema=self.schema)

        some_slice = cube.slice("product:A")
        self.assertEqual(some_slice.value, 100 + 200)

        float_value = some_slice + 100 - 100
        self.assertEqual(float_value, 100 + 200)

        derived_slice = some_slice.slice("channel:Online")
        self.assertEqual(derived_slice.value, 100)

