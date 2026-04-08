import pandas as pd
import sqlite3
import os

# =========================================================
# PATHS
# =========================================================
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "output", "cleaned")
DB_PATH   = os.path.join(BASE_DIR, "output", "olist.db")

# =========================================================
# LOAD CLEANED DATA
# =========================================================
orders      = pd.read_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"))
order_items = pd.read_csv(os.path.join(CLEAN_DIR, "order_items_clean.csv"))
payments    = pd.read_csv(os.path.join(CLEAN_DIR, "payments_clean.csv"))
reviews     = pd.read_csv(os.path.join(CLEAN_DIR, "reviews_clean.csv"))
products    = pd.read_csv(os.path.join(CLEAN_DIR, "products_clean.csv"))
customers   = pd.read_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"))
sellers     = pd.read_csv(os.path.join(CLEAN_DIR, "sellers_clean.csv"))

# =========================================================
# CREATE SQLITE DATABASE
# =========================================================
conn = sqlite3.connect(DB_PATH)

orders.to_sql("orders",           conn, if_exists="replace", index=False)
order_items.to_sql("order_items", conn, if_exists="replace", index=False)
payments.to_sql("payments",       conn, if_exists="replace", index=False)
reviews.to_sql("reviews",         conn, if_exists="replace", index=False)
products.to_sql("products",       conn, if_exists="replace", index=False)
customers.to_sql("customers",     conn, if_exists="replace", index=False)
sellers.to_sql("sellers",         conn, if_exists="replace", index=False)

print("✅ Database created:", DB_PATH)
print()

# =========================================================
# HELPER FUNCTION
# =========================================================
def run_query(title, query):
    print(f"{'='*55}")
    print(f"📌 {title}")
    print(f"{'='*55}")
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    print()
    return df

# =========================================================
# Q1 — Total Revenue, Orders, Avg Order Value
# =========================================================
run_query(
    "Q1: Overall Business KPIs",
    """
    SELECT
        COUNT(DISTINCT o.order_id)          AS total_orders,
        ROUND(SUM(oi.total_price), 2)       AS total_revenue,
        ROUND(AVG(oi.total_price), 2)       AS avg_item_price,
        ROUND(SUM(oi.total_price) /
              COUNT(DISTINCT o.order_id),2) AS avg_order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    """
)

# =========================================================
# Q2 — Monthly Revenue Trend
# =========================================================
run_query(
    "Q2: Monthly Revenue Trend",
    """
    SELECT
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS year_month,
        COUNT(DISTINCT o.order_id)                    AS num_orders,
        ROUND(SUM(oi.total_price), 2)                 AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY year_month
    ORDER BY year_month
    """
)

# =========================================================
# Q3 — Top 10 Product Categories by Revenue
# =========================================================
run_query(
    "Q3: Top 10 Categories by Revenue",
    """
    SELECT
        p.product_category_name_english     AS category,
        COUNT(oi.order_id)                  AS num_orders,
        ROUND(SUM(oi.total_price), 2)       AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY category
    ORDER BY total_revenue DESC
    LIMIT 10
    """
)

# =========================================================
# Q4 — Average Delivery Days per Review Score
# =========================================================
run_query(
    "Q4: Avg Delivery Days per Review Score",
    """
    SELECT
        r.review_score,
        COUNT(*)                                            AS num_orders,
        ROUND(AVG(
            JULIANDAY(o.order_delivered_customer_date) -
            JULIANDAY(o.order_purchase_timestamp)
        ), 1)                                               AS avg_delivery_days
    FROM orders o
    JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY r.review_score
    ORDER BY r.review_score
    """
)

# =========================================================
# Q5 — Top 10 States by Revenue
# =========================================================
run_query(
    "Q5: Top 10 States by Revenue",
    """
    SELECT
        c.customer_state                    AS state,
        COUNT(DISTINCT o.order_id)          AS num_orders,
        ROUND(SUM(oi.total_price), 2)       AS total_revenue
    FROM orders o
    JOIN customers c   ON o.customer_id  = c.customer_id
    JOIN order_items oi ON o.order_id    = oi.order_id
    GROUP BY state
    ORDER BY total_revenue DESC
    LIMIT 10
    """
)

# =========================================================
# Q6 — Payment Type Breakdown
# =========================================================
run_query(
    "Q6: Payment Type Breakdown",
    """
    SELECT
        payment_type,
        COUNT(*)                        AS num_transactions,
        ROUND(SUM(payment_value), 2)    AS total_value,
        ROUND(AVG(payment_value), 2)    AS avg_value
    FROM payments
    GROUP BY payment_type
    ORDER BY total_value DESC
    """
)

# =========================================================
# Q7 — Top 10 Sellers by Revenue
# =========================================================
run_query(
    "Q7: Top 10 Sellers by Revenue",
    """
    SELECT
        oi.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id)     AS num_orders,
        ROUND(SUM(oi.total_price), 2)   AS total_revenue
    FROM order_items oi
    JOIN sellers s ON oi.seller_id = s.seller_id
    GROUP BY oi.seller_id
    ORDER BY total_revenue DESC
    LIMIT 10
    """
)

# =========================================================
# CLOSE CONNECTION
# =========================================================
conn.close()
print("✅ SQL Analysis Complete!")