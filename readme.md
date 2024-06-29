# CubedPandas 
<picture align="center"><img alt="Pandas Logo" src="https://raw.githubusercontent.com/Zeutschler/cubedpandas/master/pages/assets/cpd_logo.jpg"></picture>

## Easy access to Pandas data

[![PyPI version](https://badge.fury.io/py/cubedpandas.svg)](https://badge.fury.io/py/cubedpandas)
[![PyPI Downloads](https://img.shields.io/pypi/dm/cubedpandas.svg?label=PyPI%20downloads)](https://pypi.org/project/cubedpandas)
[![CI - Test](https://github.com/pandas-dev/pandas/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/Zeutschler/cubedpandas/actions/workflows/unit-tests.yml)
![GitHub license](https://img.shields.io/github/license/Zeutschler/cubedpandas)   

-----------------

***Note:*** *CubedPandas is at an early stage of its development. Features are likely subject to change. 
[Ideas, Issues](https://github.com/Zeutschler/cubedpandas/issues) and 
[Feedback](https://github.com/Zeutschler/cubedpandas/discussions) are very welcome!*

CubedPandas aims to provide an ***easy, fast & fun*** approach to access data in Pandas dataframes. 
CubedPandas wraps almost any dataframe into a virtual multi-dimensional cube, which can be accessed, 
aggregated, filtered, viewed and used in a highly convenient and natural way. 

```python
# e.g. this...
value = df.loc[df['make'] == 'Porsche', 'sellingprice'].sum()
# ...turns into this
value = cdf.Porsche.sellingprice
```

CubedPandas is ***inspired by multi-dimensional OLAP databases*** (online analytical processing), which are 
typically used for reporting, business intelligence, data warehousing and financial analysis. 
Check out the samples below and give it a try.

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

# Create a dataframe with some sales data
df = pd.DataFrame({"product":  ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "channel":  ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter",  "Peter",  "Paul",   "Paul",   "Mary",   "Mary"  ],
                   "mailing":  [True,     False,    True,     False,    True,     False   ],
                   "revenue":  [100,      150,      300,      200,      250,      350     ],
                   "cost":     [50,       90,       150,      100,      150,      175     ]})

cdf = cubed(df)  # That's it! 'cdf' is now a (C)ubed(D)ata(F)rame
```

### Multi-Dimensional Cubes?
CubedPandas **automatically infers a multi-dimensional schema** from your dataframe. This schema defines 
a multi-dimensional **Cube** over your Pandas dataframe. By default, numeric columns of the dataframe 
are considered as **measures** - *the values to analyse & aggregate* - all other columns are 
considered as the **dimensions** *to filter, navigate and view the data*. The individual values in a 
dimension are called the **members** of the dimension. In the example above, `channel` is a dimension
with the 2 members `Online` and `Retail`.

But you can also define your own schema. Schemas are quite powerful and flexible, as they will allow 
you to define not only your dimensions and measures, but also custom aggregations, some business logic, 
sorting, number formating etc. Note: This feature is not yet fully available, planned for release 0.2.0.

### Cells - Numbers Please...
The key feature of CubePandas is an easy & intuitive access to individual **Cells** in 
the virtual cube. You define a multi-dimensional address and CubedPandas will evaluate and return the 
corresponding value from the underlying dataframe.

**Cells behave like numbers** (float, int), so you can use them in arithmetic operations. In the 
following examples, all addresses will refer to the exactly same data and thereby all return the same 
value of `100`. 

```python
# First, let's use Pandas to set the scene...
a = df.loc[(df['product'] == 'Apple') & (df['channel'] == 'Online') & (df['customer'] == 'Peter'), 'revenue'].sum()

# Now with CubedPandas, using a fully qualified and non-ambiguous address, order doesn't matter
a = cdf["product:Apple", "channel:Online", "customer:Peter", "revenue"]

# If there are no ambiguities in your data, you can use a shorthand address
b = cdf["Online", "Apple", "Peter", "revenue"]

# And if member values are compliant with Python naming conventions, you can use
c = cdf.Online.Apple.Peter.revenue

assert a == b == c == 100
```

### Slice The Dice

CubedPandas allows you to slice & aggregate your data in a very convenient way. If no measure is defined, first measure in 
the schema or dataframe (columns left to right) is used as the default measure, here `revenue`. So, if no measure is 
specified, the default measure is used, hence `cdf["Apple", "Online"]` is equivalent to 
`cdf["Apple", "Online", "revenue"]`.

```python
a = cdf["Online"]              # 550 = 100 + 150 + 300
b = cdf["product:Banana"]      # 650 = 300 + 350
c = cdf["Apple", "cost"]       # 100 = 100 -> explicit sum
d = cdf["Apple", "cost"].avg   # 75 = (50 + 100) / 2
e = cdf["*"]                   # 1350 -> '*' means 'all' data 
f = cdf.count                  # 6 -> returns the number of records in the cube
g = cdf["customer:P*"]         # 750 = 100 + 150 + 300 + 200  -> wildcard search
h = cdf.Peter + cdf.Mary       # 850 = (100 + 150) + (250 + 350)
i = cdf.cost                   # 715 -> sum of all records for the measure 'cost'
```

### Your feedback & ideas are very welcome!
Please help improve and extend CubedPandas with **your feedback & ideas** and use the 
[CubedPandas GitHub Issues](https://github.com/Zeutschler/cubedpandas/issues) to request new features and report bugs. 
For general questions, discussions and feedback, please use the 
[CubedPandas GitHub Discussions](https://github.com/Zeutschler/cubedpandas/discussions).

*Enjoy ... and happy cubing!*
