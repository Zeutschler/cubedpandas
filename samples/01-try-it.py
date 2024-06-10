import pandas as pd
import cubedpandas as cpd

df = pd.DataFrame({"product": ["Apple",  "Pear",   "Banana", "Apple",  "Pear",   "Banana"],
                   "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
                   "revenue":   [100,      150,      300,      200,      250,      350]})

cube = df.cubed  # that's it! You have now a multi-dimensional cube of your DataFrame. Let's play...

print(f"Total Online revenue = {cube['Online']}")           # returns 550 = 100 + 150 + 300
print(f"Total Banana revenue = {cube['product:Banana']}")   # returns 650 = 300 + 350
print(f"Online Apple revenue = {cube['Apple', 'Online']}")  # returns 100

cube['Apple', 'Online'] *= 2  # double the revenue of "Apple" in "Online" channel
del(cube['Pear'])             # delete all data for "Pear"
print(df)                     # let's check, if the DataFrame has been updated accordingly

# ...and many more possibilities to explore and process your data!