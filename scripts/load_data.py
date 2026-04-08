import pandas as pd
import os

# =========================================================
# PATH
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA = os.path.join(BASE_DIR, "data", "raw")

# =========================================================
# LOAD ALL DATASETS
# =========================================================
customers    = pd.read_csv(os.path.join(RAW_DATA, "olist_customers_dataset.csv"))
geolocation  = pd.read_csv(os.path.join(RAW_DATA, "olist_geolocation_dataset.csv"))
order_items  = pd.read_csv(os.path.join(RAW_DATA, "olist_order_items_dataset.csv"))
payments     = pd.read_csv(os.path.join(RAW_DATA, "olist_order_payments_dataset.csv"))
reviews      = pd.read_csv(os.path.join(RAW_DATA, "olist_order_reviews_dataset.csv"))
orders       = pd.read_csv(os.path.join(RAW_DATA, "olist_orders_dataset.csv"))
products     = pd.read_csv(os.path.join(RAW_DATA, "olist_products_dataset.csv"))
sellers      = pd.read_csv(os.path.join(RAW_DATA, "olist_sellers_dataset.csv"))
category_tr  = pd.read_csv(os.path.join(RAW_DATA, "product_category_name_translation.csv"))

# =========================================================
# QUICK OVERVIEW
# =========================================================
datasets = {
    "customers"   : customers,
    "geolocation" : geolocation,
    "order_items" : order_items,
    "payments"    : payments,
    "reviews"     : reviews,
    "orders"      : orders,
    "products"    : products,
    "sellers"     : sellers,
    "category_tr" : category_tr,
}

print("=" * 55)
print(f"{'Dataset':<15} {'Rows':>8} {'Columns':>8} {'Nulls':>10}")
print("=" * 55)
for name, df in datasets.items():
    total_nulls = df.isnull().sum().sum()
    print(f"{name:<15} {df.shape[0]:>8,} {df.shape[1]:>8} {total_nulls:>10,}")
print("=" * 55)

# =========================================================
# DATA TYPES CHECK
# =========================================================
print("\n--- Orders dtypes ---")
print(orders.dtypes)

print("\n--- Orders sample ---")
print(orders.head(3))

print("\n--- Order Items sample ---")
print(order_items.head(3))