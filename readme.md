<picture align="center"><img alt="Pandas Logo" src="https://raw.githubusercontent.com/Zeutschler/cubedpandas/master/pages/assets/icons/cube64.png"></picture>

# CubedPandas 

### Multi-dimensional data analysis for [Pandas](https://github.com/pandas-dev/pandas) dataframes.

[![PyPI version](https://badge.fury.io/py/cubedpandas.svg)](https://badge.fury.io/py/cubedpandas)
[![PyPI Downloads](https://img.shields.io/pypi/dm/cubedpandas.svg?label=PyPI%20downloads)](https://pypi.org/project/cubedpandas)
[![CI - Test](https://github.com/pandas-dev/pandas/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/Zeutschler/cubedpandas/actions/workflows/unit-tests.yml)
![GitHub license](https://img.shields.io/github/license/Zeutschler/cubedpandas)   

-----------------

***Note:*** CubedPandas is at an early stage of its development, and feature might be subject to change. 
[Ideas, Issues](https://github.com/Zeutschler/cubedpandas/issues) and 
[Feedback](https://github.com/Zeutschler/cubedpandas/discussions) welcome!*

CubedPandas provides an easy, intuitive, fast and fun approach to perform multi-dimensional 
numerical data analysis & processing on Pandas dataframes. CubedPandas wraps almost any
dataframe into a multi-dimensional cube, which can be aggregated, sliced, diced, filtered, 
updated and much more. 

CubedPandas is inspired by OLAP cubes (online analytical processing), which are typically used
for reporting, business intelligence, data warehousing and financial analysis purposes. 
***Just give it a try, check out the sample code below or file [01_basic_usage.py](https://github.com/Zeutschler/cubedpandas/blob/master/samples/01_basic_usage.py)***. 
   

CubedPandas is licensed under the [BSD 3-Clause License](LICENSE) and is available on 
[GitHub](https://github.com/Zeutschler/cubedpandas) and [PyPi](https://pypi.org/project/cubedpandas/).

If you have fallen in love with CubedPandas or find it otherwise valuable, please **consider to become 
CubedPandas sponsor** on [GitHub Sponsors](https://github.com/sponsors/Zeutschler) to support the further 
development of CubedPandas. 


### A. Installation

After installing CubedPandas...

```bash
pip install cubedpandas
```

...you are ready to go. "Cubing" a Pandas DataFrame is as simple as this: `cdf = cubed(df)`.
Please refer the [CubedPandas Documentation](documentation.md) for all features details and more examples.

### B. Sample Usage

```python
# 01_basic_usage.py:
import pandas as pd
from cubedpandas import cubed

df = pd.DataFrame({"product":  ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "channel":  ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter",  "Peter",  "Paul",   "Paul",   "Mary",   "Mary"  ],
                   "revenue":  [100,      150,      300,      200,      250,      350     ],
                   "cost":     [50,        90,      150,      100,      150,      175     ]})

cube = cubed(df)  # That's it! You now have multi-dimensional access to your dataframe. Let's see...

# CubedPandas automatically infers the schema from the dataframe. Numeric columns are considered as
# measures, all other columns are considered as dimensions. But you can also provide your own schema.

# 1. Getting Data
# CubedPandas is perfect for 'cell-based' data analysis. You can access individual cells of the cube
# by slicing the cube by the dimension members and the measure you want to access. The syntax is as follows:

# A full qualified address, including all dimensions and members, is the most explicit way to access a cell:
print(cube["product:Apple", "channel:Online", "customer:Peter", "revenue"])

# Another way to access the same cell is to use a dictionary-like syntax, very powerful & fast!
print(cube[{"channel":"Online", "product":"Apple", "customer":("Peter", "Paul")}, "revenue"])

# If there are no ambiguities across your entire cube (better be sure), you can also use this short form:
print(cube["Online", "Apple", "Peter", "revenue"])

# And if your member names are also compliant with Python variable naming, you can even use this form:
print(cube.Online.Apple.Peter.revenue)

# 2. Aggregations
# Cells provide aggregations over all records in the dataframe that match the given dimensions and members.
# The default and implicit aggregation function is 'sum', but you can also use 'min', 'max', 'avg', 'count', etc.
# Cells behave like floats, so you can use them in arithmetic operations.

print(cube["Online"])               # 550 = 100 + 150 + 300
print(cube["product:Banana"])       # 650 = 300 + 350
print(cube["Apple", "Online"])      # 100 = 100 -> implicit sum
print(cube["Apple", "Online"].sum)  # 100 = 100 -> explicit sum
print(cube["Apple", "cost"].avg)    # 750 = (50 + 100) / 2
print(cube["*"])                    # 1350 -> '*' is a wildcard for all members
print(cube["*"].count)              # 6 -> number of affected records
print(cube["customer:P*"])          # 750 = 100 + 150 + 300 + 200  -> wildcard search is also supported
print(cube.Peter + cube.Mary)       # 850 = (100 + 150) + (250 + 350)

# Cells can also be reused and chained to access sub-cells.
# This is especially useful and fast for more complex data structures and repeated access to the cell or sub-cells.
# As CubedPandas does some (optional) internal caching, this can speed up your processing time by factors.
online = cube["Online"]
print(online["Apple"])              # 100, the value for "Apple" in "Online" channel
print(online.Peter)                 # 250 = 100 + 150, the values for "peter" in "Online" channel
print(online.Peter.cost)            # 140 = 50 + 90, the values for "peter" in "Online" channel

# 3. Data Manipulation
# And as you expected, you can also update, delete or insert values in the underlying dataframe if you want to.
cube["Apple", "Online"] *= 1.5         # increase all revenue value of "Apple" in "Online" channel by 50%
del cube["Pear"]                       # delete all data where "product" is "Pear"
cube["product:Orange", "Online"] = 50  # NOT WORKING YET - add a new record for "Orange" in "Online" channel

print(df)  # let's check, if the dataframe has been updated as expected

# ...that's it! Thanks for trying CubedPandas. Your feedback and ideas are highly appreciated. 
```

### C. Your feedback is very welcome!
CubedPandas is still in an early stages of development. Please help improve CubedPandas and 
use the [CubedPandas GitHub Issues](https://github.com/Zeutschler/cubedpandas/issues) 
to report bugs and request new features. For general questions, discussions and feedback,
please use the [CubedPandas GitHub Discussions](https://github.com/Zeutschler/cubedpandas/discussions).
