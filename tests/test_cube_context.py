

import pandas as pd
from unittest import TestCase
from cubedpandas.cube import Cube
from cubedpandas.context import Context
from cubedpandas.common import cubed


class TestCubeContext(TestCase):
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
                {"column": "product", "alias": "p"},
                {"column": "channel", "alias": "c"}
            ],
            "measures": [
                {"column": "sales"},
                {"column": "cost"}
            ]
        }

    def test_cube_context_methods(self):
        cdf = Cube(self.df, schema=self.schema)
        c: Context = cdf.context

        self.assertEqual(c, 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c.A.B.Online, 100 + 150)


        self.assertEqual(c["A, B, C"], 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c["A, Online"], 100)
        self.assertEqual(c["A"], 100 + 200)

        self.assertEqual(c.A.B.Online, 100 + 150)
        self.assertEqual(c.A.Online + c.B.Online, 100 + 150)
        self.assertEqual(c.cost.A.B.Online, 50 + 100)
        self.assertEqual(c.product.A.B.Online, 100 + 150)
        self.assertEqual(c.product.A.B.channel.Online, 100 + 150)
        self.assertEqual(c.product.A.B.channel.Online.sales, 100 + 150)

        self.assertEqual(c.sales, 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c.product, 100 + 150 + 300 + 200 + 250+ 350)
        self.assertEqual(c.product.A, 100 + 200)
        self.assertEqual(c.A, 100 + 200)
        self.assertEqual(c.A.Online, 100)
        self.assertEqual(c.A.Online.cost, 50)
        self.assertEqual(tuple(c.A.members.row_mask), tuple([0, 3]))
        self.assertEqual(tuple(c.A.mask), tuple([0, 3]))
        self.assertEqual(tuple(c.A.Online.mask), tuple([0]))


        #self.assertEqual(cdf[{"product": "A"}], 100 + 200)
        #self.assertEqual(cdf["product:A"], 100 + 200)
        #self.assertEqual(cdf["A"], 100 + 200)

