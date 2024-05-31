# CubedPandas 
A Python library for easy and fast multi-dimensional data analysis of Pandas DataFrames.

Doing multi-dimensional data analysis with Pandas DataFrames can be cumbersome and even slow. 
CubedPandas is a library that wraps and provides a Pandas DataFrames as a multi-dimensional data cube.
This allows for an intuitive multi-dimensional data analysis. If you are familiar with
Pivot Tables in Excel or OLAP cubes, you will feel right at home with CubedPandas. 

To speed up the data analysis, CubedPandas uses caching, lazy evaluation and uses Numpy for data aggregations.
The speedup compared to a Pandas DataFrame can be significant, up to 10x or even 100x times, especially for 
larger DataFrames and repetitive access to certain dimension members.

A cube schema can be defined to customize the cube and to provide additional information about the dimensions and measures.
But it is not required, as CubedPandas can automatically infer the schema from the DataFrame: Numeric columns are treated as measures,
and non-numeric columns are treated as dimensions.

With a single line of code, you can create a cube from a Pandas DataFrame and start doing multi-dimensional 
data analysis: `cube = cubed(df)`.

CubedPandas is still in the early stages of development. The goal is to provide a
simple and fast way to do multi-dimensional data analysis with Pandas DataFrames.


## Installation
```bash
pip install cubedpandas
```

## Usage
```python
from cubedpandas import cubed
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
