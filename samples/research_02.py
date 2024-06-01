import pandas as pd
from cubedpandas import Cube
import timeit

from datasets.datasets import simple_sales, supermarket_sales, car_sales
import timeit

df, schema = supermarket_sales()
cube = Cube(df, schema=schema)

def full():
    inner_cube = Cube(df, schema=schema)
    value = inner_cube["Yangon"]  # 'Yangon' is a member of measure 'City'
    return value

def value_only():
    return cube["Yangon"]

duration = timeit.Timer('y = full()', globals=globals()).repeat(repeat=1, number=1000)[0]
print(f"1,000x create cube and read single value by cube['Yangon'] in {duration:.2f} seconds, {1000/duration:,.0f} ms/op")

duration = timeit.Timer('y = value_only()', globals=globals()).repeat(repeat=1, number=1000)[0]
print(f"1,000x read value by cube['Yangon'] in {duration:.2f} seconds, {1000/duration:,.0f} ms/op")