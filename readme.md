# CubedPandas 

## Filter faster, analyze smarter – your DataFrames deserve it!

![GitHub license](https://img.shields.io/github/license/Zeutschler/cubedpandas?color=A1C547)
![PyPI version](https://img.shields.io/pypi/v/cubedpandas?logo=pypi&logoColor=979DA4&color=A1C547)
![Python versions](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FZeutschler%2Fcubedpandas%2Fmaster%2Fpyproject.toml&query=%24%5B'project'%5D%5B'requires-python'%5D&color=A1C547)
![PyPI Downloads](https://img.shields.io/pypi/dm/cubedpandas.svg?logo=pypi&logoColor=979DA4&label=PyPI%20downloads&color=A1C547)
![GitHub last commit](https://img.shields.io/github/last-commit/Zeutschler/cubedpandas?logo=github&logoColor=979DA4&color=A1C547)
![unit tests](https://img.shields.io/github/actions/workflow/status/zeutschler/cubedpandas/python-package.yml?logo=GitHub&logoColor=979DA4&label=unit%20tests&color=A1C547)
![build](https://img.shields.io/github/actions/workflow/status/zeutschler/cubedpandas/python-package.yml?logo=GitHub&logoColor=979DA4&color=A1C547)
![documentation](https://img.shields.io/github/actions/workflow/status/zeutschler/cubedpandas/static-site-upload.yml?logo=GitHub&logoColor=979DA4&label=docs&color=A1C547&link=https%3A%2F%2Fzeutschler.github.io%2Fcubedpandas%2F)
![codecov](https://codecov.io/github/Zeutschler/cubedpandas/graph/badge.svg?token=B12O0B6F10)


-----------------

CubedPandas offer a new ***easy, fast & fun approach to filter, navigate and analyze Pandas dataframes***.
CubedPandas is inspired by the concept of [OLAP databases](https://en.wikipedia.org/wiki/Online_analytical_processing)
and aims to bring add comfort and power to Pandas dataframe handling.

For novice users, CubedPandas can be a great help to get started with Pandas, as it hides
the complexity and verbosity of Pandas dataframes. For experienced users, CubedPandas
can be a productivity booster, as it allows you to write more compact, explicit, readable and
maintainable code, e.g. this Pandas code:

```python
# Pandas: calculate the total revenue of all hybrid Audi cars in September 2024
value = df.loc[
    (df['make'] == 'Audi') &
    (df['engine'] == 'hybrid') &
    (df['date'] >= '2024-09-01') & (df['date'] <= '2024-09-30'),
    'revenue'
].sum()
```

can turn into this equivalent CubedPandas code:

```python
# with CubedPandas:
value = df.cubed.make.Audi.engine.hybrid.date.september_2024.revenue

# or maybe even shorter:
value = df.cubed.Audi.hybrid.sep_2024

# filtering dataframes is as easy as this: just add '.df' at the end
df = df.cubed.make.Audi.engine.hybrid.df
```

CubedPandas offers a fluent interface based on the data available in the underlying DataFrame.
So, filtering, navigation and analysis of Pandas dataframes becomes more intuitive, more readable and more fun.

CubedPandas neither duplicates data nor modifies the underlying DataFrame, and it introduces
no performance penalty. In fact, it can sometimes significantly speed up your data processing.

[Jupyter notebooks](https://jupyter.org) is the perfect habitat for CubedPandas. For further information,
please visit the [CubedPandas Documentation](https://zeutschler.github.io/cubedpandas/)
or try some of the included samples.

### Getting Started

CubedPandas is available on pypi.org (https://pypi.org/project/cubedpandas/) and can be installed by

```console
pip install cubedpandas
```

Using CubedPandas is as simple as wrapping any Pandas dataframe into a cube like this:

```python
import pandas as pd
from cubedpandas import cubed

# Create a dataframe with some sales data
df = pd.DataFrame({"product":  ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "channel":  ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter",  "Peter",  "Paul",   "Paul",   "Mary",   "Mary"  ],
                   "mailing":  [True,     False,    True,     False,    True,     False   ],
                   "revenue":  [100,      150,      300,      200,      250,      350     ],
                   "cost":     [50,       90,       150,      100,      150,      175     ]})

cdf = cubed(df)  # Wrapp your dataframe into a cube and start using it!
```

CubedPandas **automatically infers a multi-dimensional schema** from your Pandas dataframe which 
defines a virtual **Cube** over the dataframe. By default, numeric columns of the dataframe 
are considered as **Measures** - *the numeric values to analyse & aggregate* - all other columns are 
considered as **Dimensions** - *to filter, navigate and view the data*. The individual values in a 
dimension column are called the **Members** of the dimension. In the example above, column `channel`
becomes a dimension with the two members `Online` and `Retail`, `revenue` and `cost` are our measures.

Although rarely required, you can also define your own schema. Schemas are quite powerful and flexible, 
as they will allow you to define dimensions and measures, aliases and (planned for upcoming releases)
also custom aggregations, business logic, number formating, linked cubes (star-schemas) and much more.

### Context please, so I will give you data!
One key feature of CubePandas is an easy & intuitive access to individual **Data Cells** in
multi-dimensional data space. To do so, you'll need to define a multi-dimensional **Context** so
CubedPandas will evaluate, aggregate (`sum` by default) and return the requested value from 
the underlying dataframe.

**Context objects behave like normal numbers** (float, int), so you can use them directly in arithmetic
operations. In the following examples, all addresses will refer to the exactly same rows from the dataframe
and thereby all return the same value of `100`. 

```python
# Let Pandas set the scene...
a = df.loc[(df["product"] == "Apple") & (df["channel"] == "Online") & (df["customer"] == "Peter"), "revenue"].sum()

# Can we do better with CubedPandas? 
b = cdf["product:Apple", "channel:Online", "customer:Peter"].revenue  # explicit, readable, flexible and fast  
c = cdf.product["Apple"].channel["Online"].customer[
    "Peter"].revenue  # ...better, if column names are Python-compliant  
d = cdf.product.Apple.channel.Online.customer.Peter.revenue  # ...even better, if member names are Python-compliant

# If there are no ambiguities in your dataframe - what can be easily checked - then you can use this shorthand forms:
e = cdf["Online", "Apple", "Peter", "revenue"]
f = cdf.Online.Apple.Peter.revenue
g = cdf.Online.Apple.Peter  # as 'revenue' is the default (first) measure of the cube, it can be omitted

assert a == b == c == d == e == f == g == 100
```

Context objects also act as **filters on the underlying dataframe**. So you can use also CubedPandas for
fast and easy filtering only, e.g. like this:

```python   
df = df.cubed.product["Apple"].channel["Online"].df
df = df.cubed.Apple.Online.df  # short form, if column names are Python-compliant and there are no ambiguities
```

### Pivot, Drill-Down, Slice & Dice

The Pandas pivot table is a very powerful tool. Unfortunately, it is quite verbose and very hard to master.
CubedPandas offers the `slice` method to create pivot tables in a more intuitive and easy way, e.g. by default

```python   
# Let's create a simple pivot table with the revenue for dimensions products and channels
cdf.slice(rows="product", columns="channel", measures="revenue")
```

For further information, samples and a complete feature list as well as valuable tips and tricks,
please visit the [CubedPandas Documentation](https://zeutschler.github.io/cubedpandas/).


### Your feedback, ideas and support are very welcome!
Please help improve and extend CubedPandas with **your feedback & ideas** and use the 
[CubedPandas GitHub Issues](https://github.com/Zeutschler/cubedpandas/issues) to request new features and report bugs. 
For general questions, discussions and feedback, please use the 
[CubedPandas GitHub Discussions](https://github.com/Zeutschler/cubedpandas/discussions).

If you have fallen in love with CubedPandas or find it otherwise valuable, 
please consider to [become a sponsor of the CubedPandas project](https://github.com/sponsors/Zeutschler) so we 
can push the project forward faster and make CubePandas even more awesome.

*...happy cubing!*
