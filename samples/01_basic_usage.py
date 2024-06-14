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