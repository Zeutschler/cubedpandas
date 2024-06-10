# CubedPandas 


CubedPandas provides a simple, intuitive, fast and fun way to do multi-dimensional data analysis & manipulation with 
tabular [Pandas DataFrames](https://pandas.pydata.org), just as provided and handy for business intelligence (BI), 
data warehousing (DWH) and financial analysis & planning (CPM = corporate performance management).

CubedPandas is licensed under the [MIT License](LICENSE) and is available on 
[GitHub](https://github.com/Zeutschler/cubedpandas) and [PyPi](https://pypi.org/project/cubedpandas/).


## A. Installation and basic usage

After installing CubedPandas using pip...

```bash
pip install cubedpandas
```

...you are ready to go. "Cubing" a Pandas DataFrame is as simple as this:

```python
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
```

Please refer the [CubedPandas Documentation](documentation.md) for details and more examples.

## B. Some Background
### Why CubedPandas?
We all somehow love and hate Pandas. It's so powerful and flexible, but sometimes it's just too much or too cumbersome 
and complex to do quite simple things. As a fan of cell-based OLAP databases like IBM TM/1, Jedox PALO, Infor d/EPM, 
MS SSAS or SAP HANA, I often missed a simple, intuitive and fast way to do multi-dimensional data analysis and 
manipulation with Pandas DataFrames. So, I decided to create CubedPandas to fill this gap.

CubedPandas is not intended to replace Pandas, but to be a useful extension to it. Especially when your data and work 
benefits from multi-dimensional analysis & manipulation, requires hierarchical aggregations or otherwise cumbersome 
to implement business logic in Pandas. Cubed Pandas is aimed to offer data engineers, data scientists, business users 
more fun and productivity. ***So hopefully it helps you too.*** 

### CubedPandas - Schema, Dimensions, Measures
In BI and DWH a multi-dimensional data model requires you to define an schema, which defines the dimensions and 
measures of the data model. Although you can define your own schema on how CubedPandas should provide your DataFrame 
as a multi-dimensional cube, it is not required. Instead and by default, CubedPandas automatically
infers the dimensions and measures from the DataFrame's columns and their data types. By default, all numeric columns 
are treated as measures, while the non-numeric columns are treated as dimensions. Dimensions are typically categorical 
columns, like "product", "channel", "customer", "country", "year", "month", etc., but in general every column of a 
DataFrame can be used as a dimension in CubedPandas. The values of a dimension column are called "dimension members". 
Measures are typically numerical columns, like "revenue", "tax", "quantity", "price" etc., upon which various 
mathematical aggregations, like `sum`, `avg`, `min`, `max`, `count` etc., can be performed. The default aggregation 
in CubePandas is the `sum` aggregation, so you do not need to use `sum` keyword explicitly.

Please refer the [CubedPandas Documentation](documentation.md) for further information and guidance. 

### How it internally works
CubePandas wraps a Pandas DataFrame into a thin layer and tries to avoid any unnecessary data copy or move. 
Instead, aggregations and computations are optimized for performance and executed on-the-fly and in a lazy manner, 
most often directly on the underlying [Numpy](https://numpy.org) arrays of the DataFrame. 
As initialization (aka "cubing a DataFrame") just requires some meta-data processing, it is done in almost no time 
and you up and ready to go instantly.    

### CubedPandas can be faster than Pandas
Due to optimized data access and (optional) caching capabilities, CubedPandas can (not must) be faster  
than working with Pandas DataFrames directly. In some cases the speedup can be very significant, especially when 
certain data areas of a DataFrame, certain dimension members or individual records of larger DataFrames are 
repetitively accessed. Up to 10x or more times, depending on the use case and the data size. 
In the [samples folder](/samples/readme.md) you will find a few scripts that benchmark CubedPandas against Pandas. 

### Your feedback is very welcome and needed
CubedPandas is still in the early stages of development. Please use the [CubedPandas GitHub Issues](https://github.com/Zeutschler/cubedpandas/issues) 
to report bugs, request new features or ask questions.
