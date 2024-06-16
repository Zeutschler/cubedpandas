# cdf = cubed(df)

The `cubed` function is the most convenient way to wrap and convert a Pandas dataframe into a CubedPandas cube.
`cdf` is nice and short for a 'cubed data frame' following the Pandas convention of `df` for a 'data frame'.

If no schema is provided when applying the `cubed` method, a schema will be automatically inferred from the DataFrame. 
By default, all numeric columns will be considered as measures, all other columns as dimensions of the cube.

```python
import pandas as pd
from cubedpandas import cubed

df = pd.DataFrame({"channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "product": ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "sales":   [100,      150,      300,      200,      250,      350     ],})
cdf = cubed(df)    
print(f"Online apple sales = ${cdf.Apple.Online}")
```

Sometimes, e.g. if you want an `integer` column to be considered as a dimension, you need to provide a schema.
Here's an example of the schema with an explicit schema definition, identical to schema automatically inferred.
For more information please refer to the [Schema](class-schema.md) documentation.

```python
import pandas as pd
from cubedpandas import cubed

df = pd.DataFrame({"channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "product": ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "sales":   [100,      150,      300,      200,      250,      350     ],})
schema = {"dimensions": [{"column":"channel"}, {"column": "product"}],
          "measures":   [{"column":"sales"}]}
cdf = cubed(df, schema=schema)
print(f"Online apple sales = ${cdf.Apple.Online}")
```

The `cubed` method provides the following parameters: 

::: cubedpandas.pandas_extension.cubed





