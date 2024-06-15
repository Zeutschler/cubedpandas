import pandas as pd
from unittest import TestCase
from cubedpandas.cube import Cube
from cubedpandas.schema import Schema

class TestSchema(TestCase):
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

    def test_infer_schema(self):

        # create a cube without a schema,
        # this will force a call to Schema.infer_schema(...)
        cube = Cube(self.df)
        # get the created schema
        generated_schema = cube.schema

        # compare to expected schema
        as_is = generated_schema.to_dict()
        to_be = self.schema
        self.assertEqual(as_is, to_be)

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

    def test_cell(self):

        cube = Cube(self.df, schema=self.schema)

        some_cell = cube.cell("product:A")
        self.assertEqual(some_cell.value, 100 + 200)

        float_value = some_cell + 100 - 100
        self.assertEqual(float_value, 100 + 200)

        derived_cell = some_cell.cell("channel:Online")
        self.assertEqual(derived_cell.value, 100)

