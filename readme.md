# CubedPandas 

## OLAP comfort meets Pandas power!

![GitHub license](https://img.shields.io/github/license/Zeutschler/cubedpandas?color=A1C547)
![PyPI version](https://img.shields.io/pypi/v/cubedpandas?logo=pypi&logoColor=979DA4&color=A1C547)
![Python versions](https://img.shields.io/pypi/pyversions/cubedpandas?logo=pypi&logoColor=979DA4&color=A1C547)
![PyPI Downloads](https://img.shields.io/pypi/dm/cubedpandas.svg?logo=pypi&logoColor=979DA4&label=PyPI%20downloads&color=A1C547)
![GitHub last commit](https://img.shields.io/github/last-commit/Zeutschler/cubedpandas?logo=github&logoColor=979DA4&color=A1C547)
![unit tests](https://img.shields.io/github/actions/workflow/status/zeutschler/cubedpandas/python-package.yml?logo=GitHub&logoColor=979DA4&label=unit%20tests&color=A1C547)
![build](https://img.shields.io/github/actions/workflow/status/zeutschler/cubedpandas/python-package.yml?logo=GitHub&logoColor=979DA4&color=A1C547)
![documentation](https://img.shields.io/github/actions/workflow/status/zeutschler/cubedpandas/website.yml?logo=GitHub&logoColor=979DA4&label=docs&color=A1C547&link=https%3A%2F%2Fzeutschler.github.io%2Fcubedpandas%2F
)
![codecov](https://codecov.io/github/Zeutschler/cubedpandas/graph/badge.svg?token=B12O0B6F10)
![sponsor](https://img.shields.io/github/sponsors/zeutschler)

-----------------

***Remark:*** *CubedPandas is in an early stage of development. Features are likely subject to change. 
Anyhow, your [Ideas, Issues](https://github.com/Zeutschler/cubedpandas/issues) and [Feedback](https://github.com/Zeutschler/cubedpandas/discussions) are very welcome!

CubedPandas aims to offer an ***easy, fast & natural approach to work with Pandas dataframes***. 
To achieve this, CubedPandas wraps your dataframe into a lightweight, virtual multi-dimensional OLAP cube, 
that can be analysed and used in a very natural, compact and readable and natural manner. 

For novice users, CubedPandas can be a great help to get started with Pandas, as it hides some
of the complexity and verbosity of Pandas dataframes. For experienced users, CubedPandas
can be a great productivity booster, as it allows to write more compact, readable and
maintainable code. Just to give you a first idea, this Pandas code:

```python
value = df.loc[(df['make'] == 'Audi') & (df['engine'] == 'hybrid'), 'price'].sum()
```

can be turned into this CubedPandas code:

```python
value = df.cubed.Audi.hybrid.price
```

As CubedPandas does not duplicate data or modifies the underlying dataframe and does not add 
any performance penalty - but in some cases can even boost performance by factors - it can be 
used in production use cases without any concerns and should be of great help in many use cases. 

And in [Jupyter notebooks](https://jupyter.org), CubedPandas will really 
start to shine. For further information, please visit the 
[CubedPandas Documentation](https://zeutschler.github.io/cubedpandas/).


### Installation and Getting Started

After installing CubedPandas using `pip install cubedpandas`, you are ready to go. 
*'Cubing'* a Pandas dataframe is as simple as this:

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

cdf = cubed(df)  # Wrapp your dataframe into a cube and start cubing!
```

CubedPandas **automatically infers a multi-dimensional schema** from your Pandas dataframe which 
defines a virtual **Cube** over the dataframe. By default, numeric columns of the dataframe 
are considered as **Measures** - *the numeric values to analyse & aggregate* - all other columns are 
considered as **Dimensions** - *to filter, navigate and view the data*. The individual values in a 
dimension column are called the **Members** of the dimension. In the example above, column `channel` 
becomes a dimension with the two members `Online` and `Retail`, revenue and cost are the measures.

Although rarely required, you can also define your own schema. Schemas are quite powerful and flexible, 
as they will allow you to define dimensions and measures, aliases and (planned for upcoming releases) 
also custom aggregations, business logic, number formating, linked cubes and much more. 

### Give me a Context, so I will give you a Cell!
One key feature of CubePandas is an easy & intuitive access to individual **Data Cells** in 
multi-dimensional data space. To do so, you'll need to define a multi-dimensional **Context** and 
CubedPandas will evaluate, aggregate (`sum` by default) and return the requested value from 
the underlying dataframe.

**Context objects behave like numbers** (float, int), so you can use them directly in arithmetic 
operations. In the following examples, all addresses will refer to the exactly same rows from the dataframe
and thereby all return the same value of `100`. 

```python
# Let Pandas set the scene...
a = df.loc[(df["product"] == "Apple") & (df["channel"] == "Online") & (df["customer"] == "Peter"), "revenue"].sum()

# Can we do better with CubedPandas? 
b = cdf.product["Apple"].channel["Online"].customer["Peter"].revenue  # explicit, readable, flexible and fast  
c = cdf.product.Apple.channel.Online.customer.Peter.revenue  # identical, if member names are Python-compliant

# If there are no ambiguities in your data - can be easily checked - then you can use this shorthand forms:
d = cdf["Online", "Apple", "Peter", "revenue"]
e = cdf.Online.Apple.Peter.revenue
f = cdf.Online.Apple.Peter  # if 'revenue' is the default measure (it is), so it can be omitted

assert a == b == c == d == e == f == 100
```

Context objects act as filters on the underlying dataframe. So you can use also CubedPandas for 
fast and easy filtering only, e.g. like this:

```python   
df = df.cubed.product["Apple"].channel["Online"].df
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
