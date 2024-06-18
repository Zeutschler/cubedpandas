# Use Cases

CubedPandas is a general purpose Python library for data analysis. But in some
cases, it can be particularly useful and valuable. Here are some examples. 

If you have a creative use case of CubedPandas that you would like to share, 
please let me know. Either by leaving a comment in [CubedPandas GitHub discussions](https://github.com/Zeutschler/cubedpandas/discussions),
or by creating a [GitHub issue](https://github.com/Zeutschler/cubedpandas/issues).

## Filtering Data
CubedPandas is a great tool for just filtering data to overcome the sometimes
cumbersome Pandas syntax. You can easily filter your data by dimensions, measures,
values and conditions. You can also provide your own resolver.

e.g., if you want to filter your data for all records where the revenue is greater than 100,
you can do it like this. CubedPandas has a build in formula parser (very basic yet, more to 
come), so you can use formulas like `revenue > 100` as a filter condition. The follwing 
code will return a new Pandas dataframe containing the filtered data:
```python
cdf = cubed(df)
filtered = cdf["revenue > 100"].df
```
And do not forget, you can still use and combine this with all the other addressing methods to access cube data.
```python
cdf = cubed(df)
filtered = cdf.North_America.Retail["revenue > 42"].df
```


## Data Manipulation
Manipulatinmg data with CubedPandas is as easy as filtering. You can easily change values,
add new columns, and rows, and do most of the data manipulation tasks you can do with Pandas.

Here are some examples:
```python
cdf.revenue *= 1.1
cdf.profit = cdf.revenue - cdf.cost
```


## A. Financial Data Analysis
When it's all about the aggregation of financial and business data, CubedPandas really 
shines. As multi-dimensional addresses a re very close to our natural way of thinking,
CubedPandas is a perfect fit for reporting, business intelligence, data warehousing.

e.g., if you want then sales figure 'cars' in 'North America' for 'last month', you can
do it with CubedPandas like this:
```python
value = cube["product:cars", "region:North America", "date:last month", "sales"]
```
But stop, date is just an ordinary date column, not containing a member `last month`
but only dates like `2024-06-18`. CubedPandas is often (not always) smart enough to 
resolve waht you are looking for. In this case, it will internally translate `last month` 
to a time interval from `2024-05-01` to `2024-05-31` and return the sales figure for 
this period.

If your dataset does not has ambiguities across the dimensions of the cube (the columns 
of the underlying dataframe), you can also use this short form:   
```python
value = cube["cars", "North America", "last month", "sales"]
```
Or even, if your member names are also compliant with Python variable naming, you can
use this form:
```python
value = cube.cars.North_America.last_month.sales
```
The order of arguments is also not of importance, you can use any order you like, e.g.:
```python
value = cube.sales.last_month.cars.North_America
```

## Data Quality Analysis
CubedPandas is also a great tool for data quality analysis. You can easily check for
expected totals, missing values, duplicates, and other data quality issues.

e.g., if you want to check the total revenue measure/column for all records, you can do
it ´like this:
```python
total_revenue = cubed(df).revenue
```
If you want to find out, if there are empty values (NAN values) in the product_id dimension / column, 
you can do it and fix it like this:

```python
cdf = cubed(df)
if cdf.product_id.nan.values.any():
    cdf.product_id.nan = "unknown"
```





