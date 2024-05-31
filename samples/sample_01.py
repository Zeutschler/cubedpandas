import pandas as pd
from cubedpandas import Cube

# 0.
# Create a simple Pandas dataframe with 3 columns
data = {
    "product": ["A", "B", "C", "A", "B", "C"],
    "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
    "sales": [100, 150, 300, 200, 250, 350]
}
df = pd.DataFrame.from_dict(data)

# 1. Create a Cube wrapping the table, let the schema be inferred automatically
# -------------------------------------------------------------------------------
# You can also provide a schema explicitly, if you want to. But for now, let's keep it simple.
# By default, all string columns of a Pandas dataframe are treated as dimensions and all numerical columns as measures.
# So, a cube with 2 dimensions (products, channels) and 1 measure (sales) will be created.
cube = Cube(df)
# ...time to have some fun with your Cube

# 2. An introduction to cell-based data access
# --------------------------------------------
# Let's get the sum of all records where product = 'A'.
# As "A" is unique across all dimensions and also not the name of a measure-column, 300 will be returned.
# As 'sales' is the first and only measure in the cube, it will be returned automatically.
# If no measure is defined, always the first numerical column is used as measure.
# The default computation is 'sum', but also other statistical operations are supported.
# We'll see more of this later.
print(cube["A"])

# The following statement is identical to the previous one, but its more explicit. Especially if there are
# multiple measures. Please note that the measure always needs to be the last argument in the tuple.
print(cube["A", "sales"])

# It is recommended (and faster) to use explicit dimension names to define the dimension a member is related too.
print(cube["products:A", "sales"])

# 3. More advanced cell-based data access

# All statistical operations at work...
# ---------------------------------
print(f"Cube sum for 'A' = {cube.sum['A']}")  # 300, or just use the default method: cube['A']
print(f"Cube avg for 'A' = {cube.avg['A']}")
print(f"Cube min for 'A' = {cube.min['A']}")
print(f"Cube max for 'A' = {cube.max['A']}")
print(f"Cube count for 'A' = {cube.count['A']}")
print(f"Cube stddev for 'A' = {cube.stddev['A']}")
print(f"Cube var for 'A' = {cube.var['A']}")


print(cube[("A", "B"), "Online"])
