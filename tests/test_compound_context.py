# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

import pandas as pd
from unittest import TestCase
from cubedpandas.cube import Cube
from cubedpandas.common import cubed


class TestCompoundContext(TestCase):
    def setUp(self) -> None:
        data = {
            "product": ["A", "B", "C", "A", "B", "C"],
            "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
            "sales": [100, 150, 300, 200, 250, 350]
        }
        self.df = pd.DataFrame.from_dict(data)
        self.schema = {
            "dimensions": [
                {"column": "product"},
                {"column": "channel"}
            ],
            "measures": [
                {"column": "sales"}
            ]
        }

    def test_compound_context_creation(self):
        cdf = cubed(self.df)

        cc =cdf.product.A.by("channel")
        a = cc.get("A")

        self.assertEqual(cc.parent.address, "A")

