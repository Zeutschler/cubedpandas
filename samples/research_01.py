import pandas as pd
from cubedpandas import Cube
from datasets.datasets import simple_sales, supermarket_sales, car_sales
import timeit

df, schema = simple_sales()
cube = Cube(df, schema=schema)

def full():
    cube = Cube(df, schema=schema)
    value = cube["A"]
    value = cube["B"]
    value = cube["C"]
    value = cube["Online"]
    value = cube["Retail"]
    value = cube["A", "Online"]
    value = cube["B", "Retail"]
    return value


def value_only():
    return cube["A"]

print (timeit.Timer('y = full()', globals=globals()).repeat(repeat=1, number=1000))
duration = timeit.Timer('y = value_only()', globals=globals()).repeat(repeat=1, number=1000)[0]
print(f"Duration: {duration} seconds, {1000/duration:} ms/op")