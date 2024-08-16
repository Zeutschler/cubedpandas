import pandas as pd
import numpy as np
from cubedpandas import Cube, CachingStrategy
import timeit
import gc

size = 1_000_000

df = pd.DataFrame(np.random.randint(0,100,size=(size, 4)), columns=list('ABCD'))
value = 50
values = [50, 60, 70, 80, 90]

def pandas_one():
    mask = df['A'] == value
    return mask.index.to_numpy()
def pandas_many():
    mask = df['A'].isin(values)
    return mask.index.to_numpy()

def numpy_one():
    mask = df['A'] == value
    return mask.index.to_numpy()
def numpy_many():
    data = df["A"].to_numpy()
    mask = np.in1d(data, values)
    return mask





print("Performance comparison Pandas vs. Numpy:")
print("*"*60)
loops = 100
print(f"{size:,.0f} records in 'df' dataset.\n")

# **********************
duration = timeit.Timer('y = pandas_one()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x masking one with Pandas in {duration:.3f} seconds, "
        f"{loops/duration:,.0f} ops/sec, "
        f"{loops / duration * size:,.0f} records/sec,")

# **********************
duration = timeit.Timer('y = numpy_one()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x masking one with Numpy in {duration:.3f} seconds, "
        f"{loops/duration:,.0f} ops/sec, "
        f"{loops / duration * size:,.0f} records/sec,")


duration = timeit.Timer('y = pandas_many()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x masking many with Pandas in {duration:.3f} seconds, "
        f"{loops/duration:,.0f} ops/sec, "
        f"{loops / duration * size:,.0f} records/sec,")

# **********************
duration = timeit.Timer('y = numpy_many()', globals=globals()).repeat(repeat=1, number=loops)[0]
print(f"{loops:,.0f}x masking many with Numpy in {duration:.3f} seconds, "
        f"{loops/duration:,.0f} ops/sec, "
        f"{loops / duration * size:,.0f} records/sec,")
