from pathlib import Path

import pandas as pd

def simple_sales():
    data = {
        "product": ["A", "B", "C", "A", "B", "C"],
        "channel": ["Online", "Online", "Online", "Retail", "Retail", "Retail"],
        "sales": [100, 150, 300, 200, 250, 350]
    }
    df = pd.DataFrame.from_dict(data)
    schema = {
        "dimensions": [
            {"column": "product"},
            {"column": "channel"}
        ],
        "measures": [
            {"column": "sales"}
        ]
    }
    return df, schema

def supermarket_sales():
    # Invoice ID,Branch,City,Customer type,Gender,Product line,Unit price,Quantity,Tax 5%,Total,Date,Time,Payment,cogs,gross margin percentage,gross income,Rating
    # 750-67-8428,A,Yangon,Member,Female,Health and beauty,74.69,7,26.1415,548.9715,1/5/2019,13:08,Ewallet,522.83,4.761904762,26.1415,9.1

    df = pd.read_csv("datasets/supermarket_sales.csv")  # containing 1.000 rows
    schema = {
        "dimensions": [
            {"column": "Date"},
            {"column": "Time"},
            {"column": "Invoice ID"},
            {"column": "Branch"},
            {"column": "City"},
            {"column": "Customer type"},
            {"column": "Gender"},
            {"column": "Product line"},
            {"column": "Payment"},
        ],
        "measures": [
            {"column": "Unit price"},
            {"column": "Quantity"},
            {"column": "Tax 5%"},
            {"column": "Total"},
            {"column": "cogs"},
            {"column": "gross margin percentage"},
            {"column": "gross income"},
            {"column": "Rating"},
        ]
    }
    return df, schema

def car_sales():
    # year,make,model,trim,body,transmission,vin,state,condition,odometer,color,interior,seller,mmr,sellingprice,saledate
    # 2015,Kia,Sorento,LX,SUV,automatic,5xyktca69fg566472,ca,5,16639,white,black,kia motors america  inc,20500,21500,Tue Dec 16 2014 12:30:00 GMT-0800 (PST)
    path = Path("datasets/car_prices.csv")
    df = pd.read_csv(path)  # containing 1.000 rows
    schema = {
        "dimensions": ["year", "make" ,"model", "trim", "body", "transmission", "vin", "state", "condition",
                       "odometer", "color", "interior", "seller", "saledate"
        ],
        "measures": [ "odometer", "mmr", "sellingprice"]
    }
    return df, schema


