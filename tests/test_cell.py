# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

import pandas as pd
from unittest import TestCase
from cubedpandas import Cube


class TestCell(TestCase):
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

    def test_cell(self):

        cube = Cube(self.df, schema=self.schema)

        some_cell = cube.cell("product:A")
        self.assertEqual(some_cell.value, 100 + 200)

        float_value = some_cell + 100 - 100
        self.assertEqual(float_value, 100 + 200)

        # a cell from a cell
        derived_cell = some_cell.cell("channel:Online")
        self.assertEqual(derived_cell.value, 100)

        # direct access to 'a cell from a cell'
        self.assertEqual(some_cell["channel:Online"], 100)


    def test__derived_cell(self):
        cube = Cube(self.df, schema=self.schema)

        cell = cube.cell("product:A")
        derived_cell = cell.cell("channel:Online")
        self.assertEqual(derived_cell.value, 100)

    def test_cell_properties(self):

        cube = Cube(self.df, schema=self.schema)

        some_cell = cube.cell("product:A")
        self.assertEqual(some_cell, 100 + 200)
        self.assertEqual(some_cell.value, 100 + 200)

        self.assertEqual(some_cell.measure, "sales")
        self.assertEqual(some_cell.address, "product:A")
        self.assertEqual(some_cell.cube, cube)


    def test_cell_primary_aggregations(self):
        cube = Cube(self.df, schema=self.schema)

        a = cube.cell("product:A")  # 100 + 200 = 300
        self.assertEqual(a, 300)
        self.assertEqual(a.sum, 300)
        self.assertEqual(a.min, 100)
        self.assertEqual(a.max, 200)
        self.assertEqual(a.median, 150)
        self.assertEqual(a.std, 50)
        self.assertEqual(a.var, 2500)

        self.assertEqual(a.count, 2)
        self.assertEqual(a.an, 2)
        self.assertEqual(a.nan, 0)
        self.assertEqual(a.zero, 0)
        self.assertEqual(a.nzero, 2)

    def test_cell_secondary_aggregations(self):
        cube = Cube(self.df, schema=self.schema)

        a = cube.cell("product:A")  # 100 + 200 = 300

        self.assertEqual(a, 300)
        self.assertEqual(a["Online"], 100)  # (A, online) = 100

        self.assertEqual(a.sum["Online"], 100)
        self.assertEqual(a.min["Online"], 100)
        self.assertEqual(a.max["Online"], 100)
        self.assertEqual(a.median["Online"], 100)
        self.assertEqual(a.std["Online"], 0)
        self.assertEqual(a.var["Online"], 0)

        self.assertEqual(a.count["Online"], 1)
        self.assertEqual(a.an["Online"], 1)
        self.assertEqual(a.nan["Online"], 0)
        self.assertEqual(a.zero["Online"], 0)
        self.assertEqual(a.nzero["Online"], 1)


    def test_cell_primary_arithmetic(self):
        cube = Cube(self.df, schema=self.schema)

        a = cube.cell("product:A")  # 100 + 200 = 300
        b = cube.cell("product:B")  # 150 + 250 = 400
        self.assertEqual(a, 300)
        self.assertEqual(b, 400)

        # plus operators
        c = a + 1
        self.assertEqual(c, 300 + 1)
        c = a + b
        self.assertEqual(c, 300 + 400)
        c = a + b + 1
        self.assertEqual(c, 300 + 400 + 1)
        c += 1
        self.assertEqual(c, 300 + 400 + 1 + 1)
        c += b
        self.assertEqual(c, 300 + 400 + 1 + 1 + 400)


        # minus operators
        c = a - 1
        self.assertEqual(c, 300 - 1)
        c = a - b
        self.assertEqual(c, 300 - 400)
        c = a - b - 1
        self.assertEqual(c, 300 - 400 - 1)
        c -= 1
        self.assertEqual(c, 300 - 400 - 1 - 1)
        c -= b
        self.assertEqual(c, 300 - 400 - 1 - 1 - 400)

        # multiplication operators
        c = a * 2
        self.assertEqual(c, 300 * 2)
        c = a * b
        self.assertEqual(c, 300 * 400)
        c = a * b * 2
        self.assertEqual(c, 300 * 400 * 2)
        c *= 2
        self.assertEqual(c, 300 * 400 * 2 * 2)
        c *= b
        self.assertEqual(c, 300 * 400 * 2 * 2 * 400)

        # division operators
        c = a / 2
        self.assertEqual(c, 300 / 2)
        c = a / b
        self.assertEqual(c, 300 / 400)
        c = a / b / 2
        self.assertEqual(c, 300 / 400 / 2)
        c /= 2
        self.assertEqual(c, 300 / 400 / 2 / 2)
        c /= b
        self.assertEqual(c, 300 / 400 / 2 / 2 / 400)

        # modulo operators
        c = a % 2
        self.assertEqual(c, 300 % 2)
        c = a % b
        self.assertEqual(c, 300 % 400)
        c = a % b % 2
        self.assertEqual(c, 300 % 400 % 2)

        # power operators
        c = a ** 2
        self.assertEqual(c, 300 ** 2)


    def test_cell_secondary_arithmetic(self):
        cube = Cube(self.df, schema=self.schema)

        a = cube.cell("product:A")  # 100 + 200 = 300
        b = cube.cell("product:B")  # 150 + 250 = 400
        self.assertEqual(a, 300)
        self.assertEqual(b, 400)

        # (A, Online) = 100
        # (B, Online) = 150

        # plus operators
        c = a["Online"] + 1
        self.assertEqual(c, 100 + 1)
        c = a["Online"] + b["Online"]
        self.assertEqual(c, 100 + 150)
        c = a["Online"] + b["Online"] + 1
        self.assertEqual(c, 100 + 150 + 1)
        c += 1
        self.assertEqual(c, 100 + 150 + 1 + 1)
        c += b["Online"]
        self.assertEqual(c, 100 + 150 + 1 + 1 + 150)


        # minus operators
        c = a["Online"] - 1
        self.assertEqual(c, 100 - 1)
        c = a["Online"] - b["Online"]
        self.assertEqual(c, 100 - 150)
        c = a["Online"] - b["Online"] - 1
        self.assertEqual(c, 100 - 150 - 1)
        c -= 1
        self.assertEqual(c, 100 - 150 - 1 - 1)
        c -= b["Online"]
        self.assertEqual(c, 100 - 150 - 1 - 1 - 150)

        # multiplication operators
        c = a["Online"] * 2
        self.assertEqual(c, 100 * 2)
        c = a["Online"] * b["Online"]
        self.assertEqual(c, 100 * 150)
        c = a["Online"] * b["Online"] * 2
        self.assertEqual(c, 100 * 150 * 2)
        c *= 2
        self.assertEqual(c, 100 * 150 * 2 * 2)
        c *= b["Online"]
        self.assertEqual(c, 100 * 150 * 2 * 2 * 150)

        # division operators
        c = a["Online"] / 2
        self.assertEqual(c, 100 / 2)
        c = a["Online"] / b["Online"]
        self.assertEqual(c, 100 / 150)
        c = a["Online"] / b["Online"] / 2
        self.assertEqual(c, 100 / 150 / 2)
        c /= 2
        self.assertEqual(c, 100 / 150 / 2 / 2)
        c /= b["Online"]
        self.assertEqual(c, 100 / 150 / 2 / 2 / 150)

        # modulo operators
        c = a["Online"] % 2
        self.assertEqual(c, 100 % 2)
        c = a["Online"] % b["Online"]
        self.assertEqual(c, 100 % 150)
        c = a["Online"] % b["Online"] % 2
        self.assertEqual(c, 100 % 150 % 2)

        # power operators
        c = a["Online"] ** 2
        self.assertEqual(c, 100 ** 2)
