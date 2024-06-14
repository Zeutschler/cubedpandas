<picture align="center">
  <img alt="Pandas Logo" src="logo.jpg">
</picture>

# CubedPandas 

### Multi-dimensional data analysis for [Pandas](https://github.com/pandas-dev/pandas) dataframes.

[![PyPI Latest Release](https://img.shields.io/pypi/v/cubedpandas.svg?label=PyPI)](https://pypi.org/project/cubedpandas/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/cubedpandas.svg?label=PyPI%20downloads)](https://pypi.org/project/pandas/)
[![PyPI version](https://badge.fury.io/py/cubedpandas.svg)](https://badge.fury.io/py/cubedpandas)
[![CI - Test](https://github.com/pandas-dev/pandas/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/Zeutschler/cubedpandas/actions/workflows/unit-tests.yml)
![GitHub license](https://img.shields.io/github/license/Zeutschler/cubedpandas)   

-----------------

CubedPandas provides an easy, intuitive, fast and fun approach to perform multi-dimensional 
data analysis & processing on Pandas dataframes. CubedPandas wraps almost any
dataframe into a multi-dimensional data cube, which can be aggregated, sliced, diced, filtered, 
updated and much more. 
CubedPandas is inspired by OLAP cubes (online analytical processing), which are typically used
for reporting, business intelligence, data warehousing and financial analysis purposes. 
Just give it a try...   

CubedPandas is licensed under the [MIT License](LICENSE) and is available on 
[GitHub](https://github.com/Zeutschler/cubedpandas) and [PyPi](https://pypi.org/project/cubedpandas/).

If you faven fallen in love with CubedPandas or find it otherwise valuable, please **consider to become CubedPandas sponsor**
to support the further development of CubedPandas on [GitHub Sponsors](https://github.com/sponsors/Zeutschler). 


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

df = pd.DataFrame({"product": ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "revenue":   [100,      150,      300,      200,      250,      350]})

cube = cubed(df)  # That's it! You now have multi-dimensional access to your dataframe. Let's see...

# To return values from the cube, we need to "slice the cube" using the following syntax:
print(cube["Online"])           # 550 = 100 + 150 + 300
print(cube["product:Banana"])   # 650 = 300 + 350 using explicit dimension name (good practise & faster)
print(cube["Apple", "Online"])  # 100
print(cube[("Apple", "Banana"), "Online"])  # 400 = 100 + 300
print(cube["*"])                # 1350 (grand total)
print(cube["Apple"].avg)        # 150 = (100 + 200) / 2

online = cube["Online"]         # Slices can be sliced again (good practise & faster execution)
print(online["Apple"])          # 100, the value for "Apple" in "Online" channel

print(online["Apple"] + online["Banana"])  # 400 = 100 + 300 > Slices behave like normal numeric values

# You can also update, delete or insert values in the underlying dataframe
cube["Apple", "Online"] *= 1.5         # increase the revenue of "Apple" in "Online" channel
del cube["Pear"]                       # delete all data where "product" is "Pear"
cube["product:Orange", "Online"] = 50  # add a new record for "Orange" in "Online" channel

print(df)  # let's check, if the dataframe has been updated as expected

# ...many more possibilities to explore and process your data to come!
```

### C. Your feedback is very welcome!
CubedPandas is still in an early stages of development. Please help improve CubedPandas and 
use the [CubedPandas GitHub Issues](https://github.com/Zeutschler/cubedpandas/issues) 
to report bugs and request new features. For general questions, discussions and feedback,
please use the [CubedPandas GitHub Discussions](https://github.com/Zeutschler/cubedpandas/discussions).
