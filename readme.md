

# <picture align="center"><img alt="Pandas Logo" src="https://raw.githubusercontent.com/Zeutschler/cubedpandas/master/pages/assets/icons/cube24.png"></picture> CubedPandas 

## Multi-dimensional data analysis for Pandas dataframes.

[![PyPI version](https://badge.fury.io/py/cubedpandas.svg)](https://badge.fury.io/py/cubedpandas)
[![PyPI Downloads](https://img.shields.io/pypi/dm/cubedpandas.svg?label=PyPI%20downloads)](https://pypi.org/project/cubedpandas)
[![CI - Test](https://github.com/pandas-dev/pandas/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/Zeutschler/cubedpandas/actions/workflows/unit-tests.yml)
![GitHub license](https://img.shields.io/github/license/Zeutschler/cubedpandas)   

-----------------

***Note:*** *CubedPandas is at an early stage of its development. Features may change. 
[Ideas, Issues](https://github.com/Zeutschler/cubedpandas/issues) and 
[Feedback](https://github.com/Zeutschler/cubedpandas/discussions) are very welcome!*

CubedPandas provides an ***easy, fast & fun*** approach to perform multi-dimensional 
data analysis on Pandas dataframes. CubedPandas wraps almost any dataframe into a 
multi-dimensional cube, which can be analyzed, aggregated, sliced, filtered, viewed 
and much more. 

CubedPandas is ***inspired by OLAP databases*** (online analytical processing), which are 
typically used for reporting, business intelligence, data warehousing and financial analysis 
purposes. Check out the sample code below and ***give it a try***.

CubedPandas is licensed under the [BSD 3-Clause License](LICENSE) and is available on 
[GitHub](https://github.com/Zeutschler/cubedpandas) and [PyPi](https://pypi.org/project/cubedpandas/).

If you have fallen in love with CubedPandas or find it otherwise valuable, please **consider 
to sponsor the project** on [GitHub Sponsors](https://github.com/sponsors/Zeutschler), so many cool ideas/features to come. 


## Getting started

After installing CubedPandas...

```bash
pip install cubedpandas
```

...you are ready to go. "Cubing" a Pandas DataFrame is as simple as this:


```python
import pandas as pd
from common import cubed

df = pd.DataFrame({"product":  ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "channel":  ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter",  "Peter",  "Paul",   "Paul",   "Mary",   "Mary"  ],
                   "mailing":  [True,     False,    True,     False,    True,     False   ],
                   "revenue":  [100,      150,      300,      200,      250,      350     ],
                   "cost":     [50,       90,       150,      100,      150,      175     ]})

cdf = cubed(df)  # That's it! 'cdf' is now a CubedDataFrame
```

### Multi-Dimensional Cubes?
CubedPandas **automatically infers a multi-dimensional schema** from the dataframe. By default, numeric 
columns are considered as **measures** - *the values to analyse & aggregate* - all other columns are 
considered as the **dimensions** *to filter, navigate and view the data*. The values in the dimensions
are called **members**.

But you can also define your own schema. Schemas are quite powerful and flexible, as they will allow 
you to define not only your dimensions and measures, but also custom aggregations, some business logic, 
sorting, number formating etc. ***Note: This feature not yet available, planned for release 0.2.0***.

### Multi-Dimensional Cells - Numbers Please...
One key feature of CubePandas is its easy & intuitive access to individual data cells in the cube.
You define a multi-dimensional address and CubedPandas will evaluate and return the corresponding value.

**Cells behave like numbers** (float, int), so you can use them in arithmetic operations. In the 
following examples, all addresses will refer to the same data and return the same value of `100`. 

```python
# Using a proper, fully qualified and unambiguous address, order doesn't matter
a = cdf["product:Apple", "channel:Online", "customer:Peter", "revenue"]

# If there are no ambiguities in your data, you can use a shorthand address
b = cdf["Online", "Apple", "Peter", "revenue"]

# And if member values are compliant with Python naming conventions, you can use
c = cdf.Online.Apple.Peter.revenue

assert a == b == c  == 100
```

### It's All About Slicing & Aggregating

CubedPandas allows you to slice & dice your data. You can filter by dimensions, aggregate by 
measures in a very convenient way. The first measure in the dataframe (left to right) is used 
as the default measure, here `revenue`. So, if no measure is specified, the default measure is used,
hence `cdf["Apple", "Online"]` is equivalent to `cdf["Apple", "Online", "revenue"]`.

```python
a = cdf["Online"]              # 550 = 100 + 150 + 300
b = cdf["product:Banana"]      # 650 = 300 + 350
c = cdf["Apple", "cost"]       # 100 = 100 -> explicit sum
d = cdf["Apple", "cost"].avg   # 75 = (50 + 100) / 2
e = cdf["*"]                   # 1350 -> '*' means 'all' 
f = cdf.count                  # 6 -> number of affected records
g = cdf["customer:P*"]         # 750 = 100 + 150 + 300 + 200  -> wildcard search
h = cdf.Peter + cdf.Mary       # 850 = (100 + 150) + (250 + 350)
i = cdf.cost                   # 715 -> sum of all records for the measure 'cost'
```

### Seeing Is Believing

***Note: This feature not yet available, planned for release 0.2.0***

Pandas printing capabilities are tied to the tabular structure of a dataframe. CubedPandas 
unlocks the full potential of dataframes by providing multi-dimensional views. 
These are called **Slice** and look **like an Excel Pivot-Table**. 

The following code will **show a slice** with `product` and `customer` nested on the rows, 
`channel` on the columns, and `mailing` as a filter. The default measure `revenue` is used.

```python
cdf.slice(("product", "customer"), "channel", "mailing").show()
```

### Your feedback is very welcome!
Please help improve and extend CubedPandas with **your feedback & ideas** and use the 
[CubedPandas GitHub Issues](https://github.com/Zeutschler/cubedpandas/issues) to request new features and report bugs. 
For general questions, discussions and feedback, please use the 
[CubedPandas GitHub Discussions](https://github.com/Zeutschler/cubedpandas/discussions).

*Enjoy ... and happy cubing!*
