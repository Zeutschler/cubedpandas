# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.

import pandas as pd
from unittest import TestCase
from cubedpandas import cubed
from cubedpandas import Slice


class TestSlice(TestCase):
    def setUp(self) -> None:
        data = {
            "product": ["A", "B", "C", "A", "B", "C"],
            "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
            "sales": [100, 150, 300, 200, 250, 350],
            "cost": [50, 100, 200, 100, 150, 150]
        }
        self.df = pd.DataFrame.from_dict(data)

    def test_default_slice(self):
        c = cubed(self.df)

        s = Slice(c, "product", "channel", "sales")
        print(s)
