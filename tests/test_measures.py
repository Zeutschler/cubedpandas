# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

import pandas as pd
from unittest import TestCase
from cubedpandas import Cube


class TestMeasures(TestCase):
    def setUp(self) -> None:
        data = {
            "product": ["A", "B", "C", "A", "B", "C"],
            "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
            "sales": [100, 150, 300, 200, 250, 350],
            "cost": [50, 100, 200, 100, 150, 150]
        }
        self.df = pd.DataFrame.from_dict(data)
        self.schema = {
            "dimensions": [
                {"column": "product"},
                {"column": "channel"}
            ],
            "measures": [
                {"column": "sales"},
                {"column": "cost"}
            ]
        }

    def test_change_default_measure(self):
        cdf = Cube(self.df, schema=self.schema)

        self.assertEqual(cdf.A.Online, 100)
        cdf.measures.default = "cost"
        self.assertEqual(cdf.A.Online, 50)

        with self.assertRaises(ValueError):
            cdf.measures.default = "xxxxxxx"
