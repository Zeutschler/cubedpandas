import pandas as pd
from unittest import TestCase
from cubedpandas.cube import Cube


class TestCube(TestCase):
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

    def test_scalar_member_access(self):

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

        value = cube["A", "Online", "sales"]
        self.assertEqual(value, 100)
        value = cube["B", "Retail", "sales"]
        self.assertEqual(value, 250)


    def test_tuple_member_access(self):

        cube = Cube(self.df, schema=self.schema)

        value = cube[("A", "B"),]
        self.assertEqual(value, 100 + 200 + 150 + 250)
        value = cube[("A", "C"),]
        self.assertEqual(value, 100 + 200 + 300 + 350)
        value = cube[("A", "B", "C"),]
        self.assertEqual(value, 100 + 200 + 150 + 250 + 300 + 350)

        value = cube["Online", ("A", "B")]
        self.assertEqual(value, 100 + 150)
        value = cube[("Online", "Retail"),]
        self.assertEqual(value, 100 + 150 + 300 + 200 + 250 + 350)

        value = cube[("Online", "Retail"), ("A", "C")]
        self.assertEqual(value, 100 + 200 + 300 + 350)
    def test_cube_primary_aggregations(self):
        cube = Cube(self.df, schema=self.schema)

        # A: 100 + 200 = 300
        self.assertEqual(cube["A"], 300)
        self.assertEqual(cube["A"].sum, 300)
        self.assertEqual(cube["A"].min, 100)
        self.assertEqual(cube["A"].max, 200)
        self.assertEqual(cube["A"].median, 150)
        self.assertEqual(cube["A"].std, 50)
        self.assertEqual(cube["A"].var, 2500)

        self.assertEqual(cube["A"].count, 2)
        self.assertEqual(cube["A"].an, 2)
        self.assertEqual(cube["A"].nan, 0)
        self.assertEqual(cube["A"].zero, 0)
        self.assertEqual(cube["A"].nzero, 2)

    def test_cube_secondary_aggregations(self):
        cube = Cube(self.df, schema=self.schema)

        self.assertEqual(cube["A"], 300)
        self.assertEqual(cube["A"]["Online"], 100)  # (A, online) = 100

        self.assertEqual(cube["A"].sum["Online"], 100)
        self.assertEqual(cube["A"].min["Online"], 100)
        self.assertEqual(cube["A"].max["Online"], 100)
        self.assertEqual(cube["A"].median["Online"], 100)
        self.assertEqual(cube["A"].std["Online"], 0)
        self.assertEqual(cube["A"].var["Online"], 0)

        self.assertEqual(cube["A"].count["Online"], 1)
        self.assertEqual(cube["A"].an["Online"], 1)
        self.assertEqual(cube["A"].nan["Online"], 0)
        self.assertEqual(cube["A"].zero["Online"], 0)
        self.assertEqual(cube["A"].nzero["Online"], 1)


    def test_cube_primary_arithmetic(self):
        cube = Cube(self.df, schema=self.schema)

        self.assertEqual(cube["A"], 300)
        self.assertEqual(cube["B"], 400)

        # plus operators
        c = cube["A"] + 1
        self.assertEqual(c, 300 + 1)
        c = cube["A"] + cube["B"]
        self.assertEqual(c, 300 + 400)
        c = cube["A"] + cube["B"] + 1
        self.assertEqual(c, 300 + 400 + 1)
        c += 1
        self.assertEqual(c, 300 + 400 + 1 + 1)
        c += cube["B"]
        self.assertEqual(c, 300 + 400 + 1 + 1 + 400)


        # minus operators
        c = cube["A"] - 1
        self.assertEqual(c, 300 - 1)
        c = cube["A"] - cube["B"]
        self.assertEqual(c, 300 - 400)
        c = cube["A"] - cube["B"] - 1
        self.assertEqual(c, 300 - 400 - 1)
        c -= 1
        self.assertEqual(c, 300 - 400 - 1 - 1)
        c -= cube["B"]
        self.assertEqual(c, 300 - 400 - 1 - 1 - 400)

        # multiplication operators
        c = cube["A"] * 2
        self.assertEqual(c, 300 * 2)
        c = cube["A"] * cube["B"]
        self.assertEqual(c, 300 * 400)
        c = cube["A"] * cube["B"] * 2
        self.assertEqual(c, 300 * 400 * 2)
        c *= 2
        self.assertEqual(c, 300 * 400 * 2 * 2)
        c *= cube["B"]
        self.assertEqual(c, 300 * 400 * 2 * 2 * 400)

        # division operators
        c = cube["A"] / 2
        self.assertEqual(c, 300 / 2)
        c = cube["A"] / cube["B"]
        self.assertEqual(c, 300 / 400)
        c = cube["A"] / cube["B"] / 2
        self.assertEqual(c, 300 / 400 / 2)
        c /= 2
        self.assertEqual(c, 300 / 400 / 2 / 2)
        c /= cube["B"]
        self.assertEqual(c, 300 / 400 / 2 / 2 / 400)

        # modulo operators
        c = cube["A"] % 2
        self.assertEqual(c, 300 % 2)
        c = cube["A"] % cube["B"]
        self.assertEqual(c, 300 % 400)
        c = cube["A"] % cube["B"] % 2
        self.assertEqual(c, 300 % 400 % 2)

        # power operators
        c = cube["A"] ** 2
        self.assertEqual(c, 300 ** 2)


    def test_cube_secondary_arithmetic(self):
        cube = Cube(self.df, schema=self.schema)

        self.assertEqual(cube["A"], 300)
        self.assertEqual(cube["B"], 400)

        # (A, Online) = 100
        # (B, Online) = 150

        # plus operators
        c = cube["A"]["Online"] + 1
        self.assertEqual(c, 100 + 1)
        c = cube["A"]["Online"] + cube["B"]["Online"]
        self.assertEqual(c, 100 + 150)
        c = cube["A"]["Online"] + cube["B"]["Online"] + 1
        self.assertEqual(c, 100 + 150 + 1)
        c += 1
        self.assertEqual(c, 100 + 150 + 1 + 1)
        c += cube["B"]["Online"]
        self.assertEqual(c, 100 + 150 + 1 + 1 + 150)


        # minus operators
        c = cube["A"]["Online"] - 1
        self.assertEqual(c, 100 - 1)
        c = cube["A"]["Online"] - cube["B"]["Online"]
        self.assertEqual(c, 100 - 150)
        c = cube["A"]["Online"] - cube["B"]["Online"] - 1
        self.assertEqual(c, 100 - 150 - 1)
        c -= 1
        self.assertEqual(c, 100 - 150 - 1 - 1)
        c -= cube["B"]["Online"]
        self.assertEqual(c, 100 - 150 - 1 - 1 - 150)

        # multiplication operators
        c = cube["A"]["Online"] * 2
        self.assertEqual(c, 100 * 2)
        c = cube["A"]["Online"] * cube["B"]["Online"]
        self.assertEqual(c, 100 * 150)
        c = cube["A"]["Online"] * cube["B"]["Online"] * 2
        self.assertEqual(c, 100 * 150 * 2)
        c *= 2
        self.assertEqual(c, 100 * 150 * 2 * 2)
        c *= cube["B"]["Online"]
        self.assertEqual(c, 100 * 150 * 2 * 2 * 150)

        # division operators
        c = cube["A"]["Online"] / 2
        self.assertEqual(c, 100 / 2)
        c = cube["A"]["Online"] / cube["B"]["Online"]
        self.assertEqual(c, 100 / 150)
        c = cube["A"]["Online"] / cube["B"]["Online"] / 2
        self.assertEqual(c, 100 / 150 / 2)
        c /= 2
        self.assertEqual(c, 100 / 150 / 2 / 2)
        c /= cube["B"]["Online"]
        self.assertEqual(c, 100 / 150 / 2 / 2 / 150)

        # modulo operators
        c = cube["A"]["Online"] % 2
        self.assertEqual(c, 100 % 2)
        c = cube["A"]["Online"] % cube["B"]["Online"]
        self.assertEqual(c, 100 % 150)
        c = cube["A"]["Online"] % cube["B"]["Online"] % 2
        self.assertEqual(c, 100 % 150 % 2)

        # power operators
        c = cube["A"]["Online"] ** 2
        self.assertEqual(c, 100 ** 2)
