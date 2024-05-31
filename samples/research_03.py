import pandas as pd
from cubedpandas import Cube
import timeit

from datasets.datasets import simple_sales, supermarket_sales, car_sales
import timeit

df, schema = car_sales()
cube = Cube(df, schema=schema, enable_caching=True)

# note: default measure is 'odometer'
address = "make:BMW"
address = {"make": "BMW"}
address = (("BMW", "Toyota"), )
address = {"make": ["BMW", "Toyota"]}
address = ("make:Lexus", "model:ES 300")
address = "make:BMW", "sellingprice"             # use another measure
def create_and_read():
    inner_cube = Cube(df, schema=schema)
    value = inner_cube[address]
    return value

def read_only():
    value = cube[address]
    return value

loops = 100
records_total = len(cube)
records_used = cube.count[address]
print(f"{records_total:,.0f} records in cube, {records_used:,.0f} records related to address {address}.")


duration = timeit.Timer('y = create_and_read()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x create cube and read cube[{address}] in {duration:.3f} seconds, "
      f"{loops/duration:,.0f} ops/sec, "
      f"{loops / duration * records_used:,.0f} aggregations/sec, "
      f"{loops / duration * records_total:,.0f} processed records/sec,")

duration = timeit.Timer('y = read_only()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x read cube[{address}] in {duration:.3f} seconds, "
      f"{loops/duration:,.0f} ops/sec, "
      f"{loops / duration * records_used:,.0f} aggregations/sec, "
      f"{loops / duration * records_total:,.0f} processed records/sec,")

print(f"returned value := {read_only():,.0f}")
