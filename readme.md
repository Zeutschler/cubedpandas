# CubedPandas 
A Python library for easy and fast multi-dimensional data analysis of Pandas DataFrames.

Doing multi-dimensional data analysis with Pandas DataFrames can be cumbersome and slow. 
CubedPandas is a library that wraps a Pandas DataFrames into a multi-dimensional cube.
This allows for an intuitive multi-dimensional data analysis. If you are familiar with
Pivot Tables in Excel, you will feel right at home with CubedPandas. And if you are
familiar with OLAP cubes, you will appreciate the simplicity and speed of CubedPandas.

To speed up the data analysis, CubedPandas uses caching and lazy evaluation. This means
that the data is only aggregated when needed and the results are cached for future use.
The speedup can be significant, up to 100x times, especially for large DataFrames.

CubedPandas is still in the early stages of development. The goal is to provide a
simple and fast way to do multi-dimensional data analysis with Pandas DataFrames.


## Installation
```bash
pip install cubedpandas
```

## Usage
```python
import cubedpandas as cpd
import pandas as pd

df = pd.DataFrame({
        "product": ["Apple", "Pear", "Banana", "Apple", "Pear", "Banana"],
        "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
        "sales": [100, 150, 300, 200, 250, 350]
    })
cube = cpd.Cube(df)

print(cube["Online"])  # returns 550 = 100 + 150 + 300
print(cube["Banana"])  # returns 650 = 300 + 350
print(cube["Apple", "Online"])  # returns 100
```
