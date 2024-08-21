from PIL.ImageCms import profileToProfile

# Use Cases for CubedPandas

CubedPandas is a general purpose library that aims to offer an ***easy, fast & natural approach 
to work with Pandas dataframes***. But in some cases, CubedPandas can be particularly useful and 
valuable. Here are some examples. 

!!! note
    If you have a creative use case of CubedPandas that you would like to share, 
    please let me know, I will then add them here. You can leave me a comment in the 
    [CubedPandas GitHub discussions](https://github.com/Zeutschler/cubedpandas/discussions),
    or by creating a [GitHub issue](https://github.com/Zeutschler/cubedpandas/issues).

## Novice Pandas Users
For novice users, CubedPandas can be a great help to get started with Pandas, as it hides some
of the complexity and verbosity of Pandas dataframes. Especially for business users and citizen data analysts,
who are not so familiar with Programming, CubedPandas can be much less intimidating than using Pandas.

```python       
# Pandas code
value = df.loc[(df['make'] == 'Audi') & (df['engine'] == 'hybrid'), 'price'].sum()
    
# CubedPandas code
value = df.cubed.Audi.hybrid.price
```

## Experienced Pandas Users
For experienced users, CubedPandas can be a great productivity booster, as it allows to write more compact, 
readable and maintainable code. Experts may use CubedPandas for filtering purposes only. Example:

```python       
# Let's assume you have a data file with a 'changed' column, 
# containing timestamps like '2024-06-18T12:34:56'
# To get all records that 'changed' yesterday, you could write:
df = pd.read_csv('data.csv')).cubed.changed.yesterday.df
```

## Financial Data Analysis
When it's all about the aggregation of financial and business data, CubedPandas really shines. As 
multi-dimensional addresses are very close to our natural way of thinking, CubedPandas is a perfect 
fit for reporting, business intelligence and even (minimal) data warehousing.

First, CubePandas provides direct and intuitive access to aggregated figures, e.g.:

```python
c = cubed(df)
trucks = c.region.North_America.sbu.Trucks.sales
delta = trucks.this_year - trucks.last_year
```

Second, CubedPandas can be used to create reports and pivot-tables, e.g., you can easily
create a pivot table with the total sales per region and product:

```python
# Create a simple pivot table based on the above 'truck' filter with
# 'salesrep' and 'customer' in the rows and the last and 
# actual month sales in the columns.
trucks.pivot(c.salesrep & c.customer, c.lastmonth.sales & c.actualmonth.sales)
```

## Data Quality Analysis
CubedPandas is also a great tool for data quality analysis. Due to the cell based data access, 
expected totals, missing values, duplicates, and other data quality issues can be easily checked.

```python
c = cubed(pd.read_csv('daily_delta.csv'))
nan_count = c.revenue.NAN.count
inconsistent_records = c[c.revenue_ < c.profit_]    
```






