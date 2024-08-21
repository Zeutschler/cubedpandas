# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

# CubedPandas - Sample Application
# --------------------------------
# A minimal FastAPI server that serves a CubedPandas Slice as an HTML table.
# The slice is created from a random selection of dimensions from a
# cube based on the dataset 'data.csv'. A Bootstrap based html template
# is used for styling, see 'template.html'.

import random
import uvicorn
import socket
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

import pandas as pd
from cubedpandas import cubed

html_template = Path("template.html").read_text()
df: pd.DataFrame = pd.read_csv("data.csv")

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    # Create a cube and a random slice form the dataframe
    cdf = cubed(df, exclude=["Invoice ID", "Date", "Time"])
    rows = random.sample(cdf.dimensions.to_list(), k=random.randint(1, 4 ))
    columns = None
    if len(rows) >= 3:
        columns = rows[len(rows)-1]
        rows = rows[:len(rows)-1]
    slice = cdf.slice(rows=rows, columns=columns)

    # Return the HTML from the slice
    return html_template.format(table=slice.to_html(classes=["table", "table-sm"]))


@app.get("/logo.png", response_class=FileResponse)
async def logo():
    return  FileResponse("logo.png", media_type="image/png")


@app.get("/data.csv", response_class=FileResponse)
async def logo():
    return  FileResponse("data.csv", media_type="text/csv")


if __name__ == "__main__":
    host_name = socket.gethostbyname(socket.gethostname())
    uvicorn.run("app:app", host=host_name, port=8000, log_level="debug")
