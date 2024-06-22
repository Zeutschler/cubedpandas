# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

import pandas as pd
from common import cubed

df = pd.DataFrame({"product":  ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "channel":  ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter",  "Peter",  "Paul",   "Paul",   "Mary",   "Mary"  ],
                   "revenue":  [100,      150,      300,      200,      250,      350     ],
                   "cost":     [50,        90,      150,      100,      150,      175     ]})

cube = cubed(df)  # That's it! You now have multi-dimensional access to your dataframe. Let's see...

# CubedPandas automatically infers the schema from the dataframe. (By default) numeric columns are considered as
# measures, all other columns are considered as dimensions. But you can also provide your own schema.

# 1. Getting Data
# CubedPandas is perfect for 'cell-based' data analysis. You can access individual cells of the cube
# by slicing the cube by the dimension members and the measure you want to access. Syntax:
# 1.1 A full qualified address, the most explicit way to access a cell:
print(cube["product:Apple", "channel:Online", "customer:Peter", "revenue"]) # 100
# 1.2 Dictionary-like syntax is also supported, more powerful and flexible, but less readable:
print(cube[{"channel":"Online", "product":"Apple", "customer":("Peter", "Paul")}, "revenue"]) # 100
# 1.3 If there are no ambiguities across the columns of a dataframe (better be sure),
#     then this shorthand address form can be used, which is very convenient and readable:
print(cube["Online", "Apple", "Peter", "revenue"]) # 100
# 1.4 If member names (string values) are also compliant with Python variable naming,
#     also this super convenient form is supported:
print(cube.Online.Apple.Peter.revenue) # 100


# 2. Aggregations
# Cells provide aggregation over all records in the dataframe that match the given address.
# The default and implicit aggregation function is 'sum', but you can also use 'min', 'max',
# 'avg', 'count', etc. Cells behave like floats, so you can use them in arithmetic operations.
print(cube["Online"])               # 550 = 100 + 150 + 300
print(cube["product:Banana"])       # 650 = 300 + 350
print(cube["Apple", "cost"].sum)    # 100 = 100 -> explicit sum
print(cube["Apple", "cost"].avg)    # 75 = (50 + 100) / 2
print(cube["*"])                    # 1350 -> '*' is a wildcard for all members
print(cube["*"].count)              # 6 -> number of affected records
print(cube["customer:P*"])          # 750 = 100 + 150 + 300 + 200  -> wildcard search is also supported
print(cube.Peter + cube.Mary)       # 850 = (100 + 150) + (250 + 350)
print(cube.cost)                    # 715 -> sum of all records for the measure 'cost'

# Cells can also be reused and chained to access sub-cells.
# This is especially useful and fast for more complex data structures and repeated access to
# the cell or sub-cells. As CubedPandas does some (optional) internal caching, this may speed up
# your processing time by factors.
online = cube["Online"]
print(online["Apple"])              # 100, the value for "Apple" in "Online" channel
print(online.Peter)                 # 250 = 100 + 150, the values for "peter" in "Online" channel
print(online.Peter.cost)            # 140 = 50 + 90, the values for "peter" in "Online" channel

# ...that's it for an intro! Thanks for trying CubedPandas. Feedback and ideas very welcome.