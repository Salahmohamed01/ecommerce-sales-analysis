import pandas as pd
import os

BASE_DIR = r"D:\Data Analysis\Project"
orders  = pd.read_csv(os.path.join(BASE_DIR, "output", "cleaned", "orders_clean.csv"))
reviews = pd.read_csv(os.path.join(BASE_DIR, "output", "cleaned", "reviews_clean.csv"))

orders["order_purchase_timestamp"]      = pd.to_datetime(orders["order_purchase_timestamp"])
orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])

orders["delivery_days"] = (
    orders["order_delivered_customer_date"] -
    orders["order_purchase_timestamp"]
).dt.days

merged = orders.merge(reviews[["order_id","review_score"]], on="order_id")
result = merged.groupby("review_score")["delivery_days"].mean().round(1)
print(result)