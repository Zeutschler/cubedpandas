# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

import pandas as pd
from unittest import TestCase
from cubedpandas.common import cubed
from cubedpandas.cube import Cube
from cubedpandas.filter import Filter
from cubedpandas.dimension import Dimension
from cubedpandas.measure import Measure


class TestFilter(TestCase):
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

    def test_simple_member_filter(self):
        cdf = cubed(self.df)
        product: Dimension = cdf.product
        channel: Dimension = cdf.channel

        filter = cdf.sales.as_filter > 100
        value = cdf[filter]
        self.assertEqual(value, 150 + 300 + 200 + 250 + 350)

        self.assertEqual(cdf[cdf.sales._ > 100], 150 + 300 + 200 + 250 + 350)

        self.assertEqual(cdf[cdf.sales_ > 100], 150 + 300 + 200 + 250 + 350)


        value = cdf[product.A & channel.Online]
        self.assertEqual(value, 100)

        value = cdf[channel.Online & (cdf.sales.as_filter > 100)]
        self.assertEqual(value, 150 + 300)

        value = cdf.sales
        self.assertEqual(value, 100 + 150 + 300 + 200 + 250 + 350)

        value = cdf[product.A , "Online"]
        self.assertEqual(value, 100)
