import pandas as pd
from unittest import TestCase
from cubedpandas import Cube


class TestSlice(TestCase):
    def setUp(self) -> None:
        data = {
            "product": ["A", "B", "C", "A", "B", "C"],
            "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
            "sales": [100, 150, 300, 200, 250, 350]
        }
        self.df = pd.DataFrame.from_dict(data)
        self.schema = {
            "dimensions": [
                {"column":"product"},
                {"column": "channel"}
            ],
            "measures": [
                {"column":"sales"}
            ]
        }

    def test_slice(self):

        cube = Cube(self.df, schema=self.schema)

        some_slice = cube.slice("product:A")
        self.assertEqual(some_slice.value, 100 + 200)

        float_value = some_slice + 100 - 100
        self.assertEqual(float_value, 100 + 200)

        # a slice from a slice
        derived_slice = some_slice.slice("channel:Online")
        self.assertEqual(derived_slice.value, 100)

        # direct access to 'a slice from a slice'
        self.assertEqual(some_slice["channel:Online"], 100)
