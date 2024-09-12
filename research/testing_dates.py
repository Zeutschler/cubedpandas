from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import datetime

today = datetime.now()

# 1 month ago
print(today - relativedelta(months=-1))
args=["2021-07-01","week", "last week", "last month", "last year", "yesterday", "today", "tomorrow", "next week", "next month", "next year"]
for arg in args:
    try:
        print(f"parse '{arg} := {parse(arg)}")
    except Exception as e:
        print(f"parse '{arg} := Error {e}")


