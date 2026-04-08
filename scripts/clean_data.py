import pandas as pd
import os

# =========================================================
# PATHS
# =========================================================
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA  = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "output", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)

# =========================================================
# LOAD
# =========================================================
customers   = pd.read_csv(os.path.join(RAW_DATA, "olist_customers_dataset.csv"))
order_items = pd.read_csv(os.path.join(RAW_DATA, "olist_order_items_dataset.csv"))
payments    = pd.read_csv(os.path.join(RAW_DATA, "olist_order_payments_dataset.csv"))
reviews     = pd.read_csv(os.path.join(RAW_DATA, "olist_order_reviews_dataset.csv"))
orders      = pd.read_csv(os.path.join(RAW_DATA, "olist_orders_dataset.csv"))
products    = pd.read_csv(os.path.join(RAW_DATA, "olist_products_dataset.csv"))
sellers     = pd.read_csv(os.path.join(RAW_DATA, "olist_sellers_dataset.csv"))
category_tr = pd.read_csv(os.path.join(RAW_DATA, "product_category_name_translation.csv"))

# =========================================================
# 1. ORDERS — fix dtypes + handle nulls
# =========================================================
date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

before = len(orders)
orders = orders[
    ~((orders["order_status"] == "delivered") &
      (orders["order_delivered_customer_date"].isnull()))
]
print(f"Orders: removed {before - len(orders)} delivered rows with no delivery date")
print(f"Remaining nulls in orders:\n{orders.isnull().sum()}\n")

# =========================================================
# 2. REVIEWS — drop الـ comment columns بس مش الصف كله
# =========================================================
reviews["review_comment_title"]   = reviews["review_comment_title"].fillna("")
reviews["review_comment_message"] = reviews["review_comment_message"].fillna("")

review_dates = ["review_creation_date", "review_answer_timestamp"]
for col in review_dates:
    reviews[col] = pd.to_datetime(reviews[col], errors="coerce")

print(f"Reviews nulls after fix:\n{reviews.isnull().sum()}\n")

# =========================================================
# 3. PRODUCTS — merge مع الترجمة + fill nulls
# =========================================================
products = products.merge(category_tr, on="product_category_name", how="left")
products["product_category_name_english"] = (
    products["product_category_name_english"].fillna("unknown")
)
products["product_category_name"] = (
    products["product_category_name"].fillna("unknown")
)

dim_cols = [
    "product_weight_g", "product_length_cm",
    "product_height_cm", "product_width_cm"
]
for col in dim_cols:
    products[col] = products[col].fillna(products[col].median())

print(f"Products nulls after fix:\n{products.isnull().sum()}\n")

# =========================================================
# 4. ORDER ITEMS — add total price column
# =========================================================
order_items["total_price"] = order_items["price"] + order_items["freight_value"]

# =========================================================
# 5. DUPLICATES CHECK
# =========================================================
print("=== Duplicates Check ===")
for name, df in [("orders", orders), ("customers", customers),
                 ("order_items", order_items), ("payments", payments)]:
    dups = df.duplicated().sum()
    print(f"{name}: {dups} duplicates")

# =========================================================
# 6. SAVE CLEANED FILES
# =========================================================
orders.to_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"), index=False)
order_items.to_csv(os.path.join(CLEAN_DIR, "order_items_clean.csv"), index=False)
payments.to_csv(os.path.join(CLEAN_DIR, "payments_clean.csv"), index=False)
reviews.to_csv(os.path.join(CLEAN_DIR, "reviews_clean.csv"), index=False)
products.to_csv(os.path.join(CLEAN_DIR, "products_clean.csv"), index=False)
customers.to_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"), index=False)
sellers.to_csv(os.path.join(CLEAN_DIR, "sellers_clean.csv"), index=False)

# =========================================================
# 7. DELIVERY VS REVIEW — READY FOR POWER BI
# =========================================================
orders["delivery_days"] = (
    orders["order_delivered_customer_date"] -
    orders["order_purchase_timestamp"]
).dt.days

delivery_vs_review = (
    orders[orders["order_status"] == "delivered"]
    .merge(reviews[["order_id", "review_score"]], on="order_id")
    .groupby("review_score")["delivery_days"]
    .mean()
    .round(1)
    .reset_index()
)
delivery_vs_review.columns = ["review_score", "avg_delivery_days"]
delivery_vs_review.to_csv(os.path.join(CLEAN_DIR, "delivery_vs_review.csv"), index=False)
print("✅ delivery_vs_review.csv saved!")

print("\n✅ All cleaned files saved to output/cleaned/")