import pandas as pd

from cubedpandas import cubed

df = pd.DataFrame({"product": ["Apple", "Pear", "Banana", "Apple", "Pear", "Banana"],
                   "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "customer": ["Peter", "Peter", "Paul", "Paul", "Mary", "Mary"],
                   "sales": [100, 150, 300, 200, 250, 350],
                   "cost": [50, 90, 150, 100, 150, 175]})

cdf = cubed(df)

cdf.settings.debug_mode = True
context = cdf.product["Apple", "Pear"].sales
print(context.address)

print(context.dsf_asdfsd)

value = df.loc[(df['make'] == 'Audi') &
               (df['engine'] == 'hybrid') &
               (df['date'] >= '2024-09-01') & (df['date'] <= '2024-09-30'),
'price'].sum()
