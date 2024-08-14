

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

    def test_cube_context_dynamic_methods(self):
        c = Cube(self.df, schema=self.schema)

        self.assertEqual(c.context, 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c.A.B.Online, 100 + 150)

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

    def test_cube_context_slicer_methods(self):
        c = Cube(self.df, schema=self.schema)

        with self.assertRaises(ValueError):
            a = c["XXX"]
        with self.assertRaises(ValueError):
            a = c.xxx

        self.assertEqual(c["A, B, C"], 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c["A, Online"], 100)
        self.assertEqual(c["A"], 100 + 200)

    def test_cube_context_dimension_list_methods(self):
        c = Cube(self.df, schema=self.schema)

        # 3 list variants: implicit tuple, explicit tuple, explicit list
        self.assertEqual(c.product["A", "B", "C"], 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c.product["A", "B"], 100 + 150 + 200 + 250)

        self.assertEqual(c.product[("A", "B", "C")], 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c.product[("A", "B")], 100 + 150 + 200 + 250)

        self.assertEqual(c.product[["A", "B", "C"]], 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c.product[["A", "B"]], 100 + 150 + 200 + 250)

        # special case, non-existing members like 'XXX' will be ignored.
        self.assertEqual(c.product["A", "XXX"], 100 + 200 )
        self.assertEqual(c.product[["A", "B", "XXX"]], 100 + 150 + 200 + 250)

        # special case, member list containing unhashable objects will raise ValueError
        with self.assertRaises(ValueError):
            a = c.product["A", {"not-exists":"XXX"}]  # unhashable object

    def test_cube_context_cube_list_methods(self):
        c = Cube(self.df, schema=self.schema)

        # 3 list variants: implicit tuple, explicit tuple, explicit list
        self.assertEqual(c["A", "B", "C"], 100 + 150 + 300 + 200 + 250 + 350)
        self.assertEqual(c["A", "B"], 100 + 150 + 200 + 250)

        self.assertEqual(c["A", "Online"], 100 )
        self.assertEqual(c["A", "B", "Online"], 100 + 150)

        # special case: dimension content switch from 'product' to 'channel' to 'product'
        self.assertEqual(c["A", "Online", "B"], 0) # no data, as intersection of 'A' and 'B' is always empty
        self.assertEqual(c["A", "Online", "A"], 100) # intersection of 'A' and 'A' does not change the result


    def test_cube_context_with_dim_hints_methods(self):
        c = Cube(self.df, schema=self.schema)

        self.assertEqual(c["product:A"], 100 + 200)
        self.assertEqual(c["product:A", "Online"], 100)

    def test_cube_context_with_context_arguments(self):
        c = Cube(self.df, schema=self.schema)

        # define a context filter
        filter = c.A

        self.assertEqual(c[filter], 100 + 200)
        self.assertEqual(c[filter, "Online"], 100)
        self.assertEqual(c[filter, "B", "Online"], 100 + 150) # filter and 'B' are from the same dimension, so they get joined
        self.assertEqual(c["B", filter, "Online"], 100) # todo: filter overrides the 'B' dimension, so the result is not the same as above. What to do?

        filter = c.A.Online
        self.assertEqual(c[filter, "cost"], 50)

    def test_cube_context_dict_methods(self):
        c = Cube(self.df, schema=self.schema)

        self.assertEqual(c[{"product": "A"}], 100 + 200)
        self.assertEqual(c[{"product": ["A", "B"]}], 100 + 150 + 200 + 250)
        self.assertEqual(c[{"product": "A", "channel": "Online"}], 100 )
        self.assertEqual(c[{"product": "A", "channel": ["Online", "Retail"]}], 100 + 200 )
        self.assertEqual(c[{"product": ["A", "B"], "channel": ["Online", "Retail"]}], 100 + 150 + 200 + 250 )
