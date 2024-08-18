
import pandas as pd
from cubedpandas import cubed, Context, CubeContext, MeasureContext

df = pd.DataFrame({"product": ["Apple", "Pear", "Banana", "Apple", "Pear", "Banana"],
                   "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter", "Peter", "Paul", "Paul", "Mary", "Mary"],
                   "sales": [100, 150, 300, 200, 250, 350],
                   "cost": [50, 90, 150, 100, 150, 175]})

cdf = cubed(df)  # That's it! You now have multi-dimensional access to your dataframe. Let's see...

context = cdf.product["Apple", "Pear"].sales
print(context.address)
print(context.cube_address)












