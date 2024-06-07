import pandas as pd
from cubedpandas import Cube, CachingStrategy
import timeit
import gc

from datasets.datasets import simple_sales, supermarket_sales, car_sales
import timeit

df, schema = car_sales()
use_schema = False
if use_schema:
    cube = Cube(df, schema=schema, caching=CachingStrategy.NONE)
else:
    cube = Cube(df, caching=CachingStrategy.NONE)

caching_strategy = CachingStrategy.LAZY
if use_schema:
    cached_cube = Cube(df, schema=schema, caching=caching_strategy)
else:
    cached_cube = Cube(df, caching=caching_strategy)

# note: default measure is 'odometer'
# address = {"make": "BMW"}
# address = (("BMW", "Toyota"), )
# address = {"make": ["BMW", "Toyota"]}
# address = ("make:Lexus", "model:ES 300")
# address = "make:BMW"
address = "make:BMW", "sellingprice"    # use another measure
measure = "sellingprice"

# value = df.cubed["make:BMW", "sellingprice"]

def normal_read():
    value = cube[address]
    return value

def cached_read():
    value = cached_cube[address]
    return value

def df_read():
    value = df.loc[df['make'] == 'BMW', measure].sum()
    return value

# **********************
print("Performance comparison CubedPandas cube vs. Pandas dataframe:")
print("*"*60)
loops = 100
records_total = len(cube)
records_used = cube.count[address]
print(f"{records_total:,.0f} records in 'car_sales' dataset, {records_used:,.0f} records are determined by the address {address}.\n")

# **********************
duration = timeit.Timer('y = df_read()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x direct read from dataframe in {duration:.3f} seconds, "
      f"{loops/duration:,.0f} ops/sec, "
      f"{loops / duration * records_used:,.0f} aggregations/sec, "
      f"{loops / duration * records_total:,.0f} processed records/sec,")

duration = timeit.Timer('y = normal_read()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x read cube[{address}] caching 'NONE' in {duration:.3f} seconds, "
      f"{loops/duration:,.0f} ops/sec, "
      f"{loops / duration * records_used:,.0f} aggregations/sec, "
      f"{loops / duration * records_total:,.0f} processed records/sec,")

duration = timeit.Timer('y = cached_read()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x read cube[{address}] caching '{caching_strategy}' in {duration:.3f} seconds, "
      f"{loops/duration:,.0f} ops/sec, "
      f"{loops / duration * records_used:,.0f} aggregations/sec, "
      f"{loops / duration * records_total:,.0f} processed records/sec,")

# **********************
print(f"\nreturned normal value    := {normal_read():,.0f}")
print(f"returned cached value    := {cached_read():,.0f}")
print(f"expected value (from df) := {df_read():,.0f}")

print ("\nMemory footprint:")
collected = gc.collect()
print(f"\tdataframe  : {df.memory_usage(deep=True).sum():,.0f} bytes")
print(f"\tnormal cube: {cube.memory_usage:,.0f} bytes")
print(f"\tcached cube: {cached_cube.memory_usage:,.0f} bytes")