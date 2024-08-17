# CubedPandas 

## Multi-dimensional data analysis for Pandas dataframes.

![PyPI version](https://badge.fury.io/py/cubedpandas.svg)
![PyPI Downloads](https://img.shields.io/pypi/dm/cubedpandas.svg?label=PyPI%20downloads)
![GitHub last commit](https://img.shields.io/github/last-commit/Zeutschler/cubedpandas)
![CI - Test](https://github.com/pandas-dev/pandas/actions/workflows/unit-tests.yml/badge.svg)
![build](https://img.shields.io/github/actions/workflow/status/zeutschler/cubedpandas/python-package.yml)
![codecov](https://codecov.io/github/Zeutschler/cubedpandas/graph/badge.svg?token=B12O0B6F10)
![Python versions](https://img.shields.io/pypi/pyversions/cubedpandas)
![GitHub license](https://img.shields.io/github/license/Zeutschler/cubedpandas)
![sponsor](https://img.shields.io/github/sponsors/zeutschler)

-----------------

***Remark:*** *CubedPandas is in an early stage of its development. Features are likely subject to change. 
But it's worth an early try. Your [Ideas, Issues](https://github.com/Zeutschler/cubedpandas/issues) and 
[Feedback](https://github.com/Zeutschler/cubedpandas/discussions) are very welcome!*

CubedPandas aims to provide an ***easy, fast & fun*** approach to access and analyse data in Pandas dataframes. 
CubedPandas wraps almost any dataframe into a virtual multi-dimensional cube, which can be accessed, 
aggregated, filtered, viewed and used in a highly convenient and natural way. A simple example: 

```python
# this...
value = df.loc[df['make'] == 'Audi', 'price'].sum()
# ...can turn into this.
value = cdf.Audi.price
```

CubedPandas is inspired by [multi-dimensional OLAP Cubes](https://en.wikipedia.org/wiki/Online_analytical_processing), 
which are typically used for business intelligence, data warehousing,reporting, planning and financial analysis.
Cubed Pandas is also very lightweight, as data is not no unnecessary copied or transformed, but accessed directly 
from the underlying dataframe. And it can be also quite fast, as it uses efficient filtering and can leverage
clever caching to boost performance by factors. CubedPandas is available on [GitHub](https://github.com/Zeutschler/cubedpandas) and [PyPi](https://pypi.org/project/cubedpandas/). 

### Installation and Getting Started

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

### Multi-dimensional OLAP Cubes - What the heck is that?
CubedPandas **automatically infers a multi-dimensional schema** from your Pandas dataframe. This schema 
then defines a multi-dimensional **Cube** over the dataframe. By default, numeric columns of the dataframe 
are considered as **measures** - *the numeric values to analyse & aggregate* - all other columns are 
considered as **dimensions** - *to filter, navigate and view the data*. The individual values in a 
dimension column are called the **members** of the dimension. In the example above, column `channel` 
becomes a dimension with the 2 members `Online` and `Retail`.

But you can also define your own schema. Schemas are quite powerful and flexible, as they will allow 
you to define not only your dimensions and measures, but also aliases, custom aggregations, business logic, 
sorting, number formating etc. Note: As of today, this feature is only partially implemented and planned 
for an upcoming release.

### Context please...
The key feature of CubePandas is an easy & intuitive access to individual **Data Cells** in 
the virtual multi-dimensional data space of a cube. You'll need to define a multi-dimensional **Context** and 
CubedPandas will evaluate, aggregate and return its corresponding value from the underlying dataframe.

**Context objects behave like numbers** (float, int), so you can use them in any arithmetic operations. In the 
following examples, all addresses will refer to the exactly same data and thereby all return the same 
value of `100`. 

```python
# First, let Pandas set the scene...
a = df.loc[(df["product"] == "Apple") & (df["channel"] == "Online") & (df["customer"] == "Peter"), "revenue"].sum()

# Now, let's do the same thing with CubedPandas and 'cube' your dataframe...
cdf = cubed(df)

# The best and recommended way to define a context, is to aim for a non-ambiguous context 
# that defines the requested dimensions, their members and a measure to be returned.
b = cdf.product["Apple"].channel["Online"].customer["Peter"].revenue    # optimal way, best readability
c = cdf["product:Apple", "channel:Online", "customer:Peter", "revenue"] # as a list or tuple
d = cdf[{"product": "Apple", "channel": "Online", "customer": "Peter", "measure": "revenue"}] # as a dictionary 
e = cdf.product.Apple.channel.Online.customer.Peter.revenue  # also possible, if member names are Python-compliant

# If there are no ambiguities in your data, you can also use shorthand contexts
f = cdf["Online", "Apple", "Peter", "revenue"]
g = cdf.Online.Apple.Peter.revenue
h = cdf.Online.Apple.Peter # if the measure is the default measure ('revenue' is), it can be omitted

assert a == b == c == d == e == f == g ==  h == 100
```

### Aggregations, slicing, dicing and much more...

CubedPandas allows you to slice & aggregate your data in a very convenient and flexible way. Some examples:

```python
a = cdf["Online"]              # 550 = 100 + 150 + 300
b = cdf["product:Banana"]      # 650 = 300 + 350
c = cdf["Apple", "cost"]       # 100 = 100 -> explicit sum
d = cdf["Apple", "cost"].avg   # 75 = (50 + 100) / 2
e = cdf.revenue                # 1350 -> all records for the measure 'revenue' 
f = cdf.revenue.count          # 6 -> returns the number of records in the cube
g = cdf["customer:P*"]         # 750 = 100 + 150 + 300 + 200  -> wildcard search for Peter and Paul
h = cdf.Peter + cdf.Mary       # 850 = (100 + 150) + (250 + 350)
i = cdf.cost                   # 715 -> sum of all records for the measure 'cost'
```

For all the features, more information, cool capabilities and use cases as well as valuable tips and tricks, 
please visit the [CubedPandas Documentation](https://zeutschler.github.io/cubedpandas/).


### Your feedback, ideas and support are very welcome!
Please help improve and extend CubedPandas with **your feedback & ideas** and use the 
[CubedPandas GitHub Issues](https://github.com/Zeutschler/cubedpandas/issues) to request new features and report bugs. 
For general questions, discussions and feedback, please use the 
[CubedPandas GitHub Discussions](https://github.com/Zeutschler/cubedpandas/discussions).

If you have fallen in love with CubedPandas or find it otherwise valuable, 
please consider to [become a sponsor of the CubedPandas project](https://github.com/sponsors/Zeutschler).

*...happy cubing!*
