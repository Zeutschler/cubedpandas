# Temporary research and evaluations goes here...

import pandas as pd
from cubedpandas import cubed
from cubedpandas import Context

# Load the sample dataset
df = pd.DataFrame({"product": ["Apple", "Pear", "Banana", "Apple", "Pear", "Banana"],
                   "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter", "Peter", "Paul", "Paul", "Mary", "Mary"],
                   "revenue": [100, 150, 300, 200, 250, 350],
                   "cost": [50, 90, 150, 100, 150, 175]})
cdf = cubed(df)
cdf.settings.populate_members = False

product: Context = cdf.product
print(product.Apple.Banana.Pear)