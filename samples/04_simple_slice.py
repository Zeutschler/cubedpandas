# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file
from datetime import datetime

import pandas as pd
from cubedpandas import cubed
from cubedpandas import Slice


df = pd.DataFrame({"product": ["Apple", "Pear", "Banana", "Apple", "Pear", "Banana"],
                   "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter", "Peter", "Paul", "Paul", "Mary", "Mary"],
                   "revenue": [100, 150, 300, 200, 250, 350],
                   "cost": [50, 90, 150, 100, 150, 175]})
cdf = cubed(df)

# defined slice
slice = Slice(cdf, rows=[dim for dim in cdf.dimensions], columns=cdf.measures)
slice.show()
print(slice.to_html())

slice = Slice(cdf.Online, rows=cdf.dimensions, columns=cdf.measures)
slice.show()

