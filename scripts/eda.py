import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# =========================================================
# PATHS
# =========================================================
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "output", "cleaned")
PLOTS_DIR = os.path.join(BASE_DIR, "output", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# =========================================================
# LOAD CLEANED DATA
# =========================================================
orders      = pd.read_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"),      parse_dates=["order_purchase_timestamp","order_approved_at","order_delivered_carrier_date","order_delivered_customer_date","order_estimated_delivery_date"])
order_items = pd.read_csv(os.path.join(CLEAN_DIR, "order_items_clean.csv"))
payments    = pd.read_csv(os.path.join(CLEAN_DIR, "payments_clean.csv"))
reviews     = pd.read_csv(os.path.join(CLEAN_DIR, "reviews_clean.csv"))
products    = pd.read_csv(os.path.join(CLEAN_DIR, "products_clean.csv"))
customers   = pd.read_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"))
sellers     = pd.read_csv(os.path.join(CLEAN_DIR, "sellers_clean.csv"))

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

# =========================================================
# 1. MONTHLY ORDERS TREND
# =========================================================
orders["year_month"] = orders["order_purchase_timestamp"].dt.to_period("M")
monthly = (orders.groupby("year_month")
                 .size()
                 .reset_index(name="num_orders"))
monthly["year_month_dt"] = monthly["year_month"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(monthly["year_month_dt"], monthly["num_orders"], marker="o", linewidth=2, color="#2196F3")
ax.fill_between(monthly["year_month_dt"], monthly["num_orders"], alpha=0.1, color="#2196F3")
ax.set_title("Monthly Orders Trend", fontsize=16, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Number of Orders")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "01_monthly_orders_trend.png"))
plt.close()
print("✅ Plot 1 saved: Monthly Orders Trend")

# =========================================================
# 2. MONTHLY REVENUE TREND
# =========================================================
orders_items_merged = order_items.merge(
    orders[["order_id", "order_purchase_timestamp"]], on="order_id"
)
orders_items_merged["year_month"] = pd.to_datetime(
    orders_items_merged["order_purchase_timestamp"]
).dt.to_period("M")

monthly_revenue = (orders_items_merged.groupby("year_month")["total_price"]
                                      .sum()
                                      .reset_index())
monthly_revenue["year_month_dt"] = monthly_revenue["year_month"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(monthly_revenue["year_month_dt"], monthly_revenue["total_price"], marker="o", linewidth=2, color="#4CAF50")
ax.fill_between(monthly_revenue["year_month_dt"], monthly_revenue["total_price"], alpha=0.1, color="#4CAF50")
ax.set_title("Monthly Revenue Trend", fontsize=16, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (BRL)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "02_monthly_revenue_trend.png"))
plt.close()
print("✅ Plot 2 saved: Monthly Revenue Trend")

# =========================================================
# 3. TOP 10 PRODUCT CATEGORIES
# =========================================================
top_categories = (order_items.merge(products[["product_id","product_category_name_english"]], on="product_id")
                              .groupby("product_category_name_english")["total_price"]
                              .sum()
                              .sort_values(ascending=False)
                              .head(10)
                              .reset_index())

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=top_categories, x="total_price", y="product_category_name_english",
            hue="product_category_name_english", palette="Blues_r", legend=False, ax=ax)
ax.set_title("Top 10 Product Categories by Revenue", fontsize=16, fontweight="bold")
ax.set_xlabel("Total Revenue (BRL)")
ax.set_ylabel("Category")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "03_top10_categories.png"))
plt.close()
print("✅ Plot 3 saved: Top 10 Categories by Revenue")

# =========================================================
# 4. REVIEW SCORE DISTRIBUTION
# =========================================================
fig, ax = plt.subplots(figsize=(8, 5))
score_counts = reviews["review_score"].value_counts().sort_index()
colors = ["#ef5350","#ef9a9a","#ffee58","#aed581","#66bb6a"]
ax.bar(score_counts.index, score_counts.values, color=colors, edgecolor="white", linewidth=0.8)
ax.set_title("Review Score Distribution", fontsize=16, fontweight="bold")
ax.set_xlabel("Score")
ax.set_ylabel("Number of Reviews")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for i, (score, count) in enumerate(score_counts.items()):
    ax.text(score, count + 200, f"{count:,}", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "04_review_scores.png"))
plt.close()
print("✅ Plot 4 saved: Review Score Distribution")

# =========================================================
# 5. DELIVERY TIME VS REVIEW SCORE
# =========================================================
orders_delivered = orders[orders["order_status"] == "delivered"].copy()
orders_delivered["delivery_days"] = (
    orders_delivered["order_delivered_customer_date"] -
    orders_delivered["order_purchase_timestamp"]
).dt.days

delivery_vs_review = (orders_delivered.merge(reviews[["order_id","review_score"]], on="order_id")
                                       .dropna(subset=["delivery_days"]))
avg_delivery = delivery_vs_review.groupby("review_score")["delivery_days"].mean().reset_index()

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=avg_delivery, x="review_score", y="delivery_days",
            hue="review_score", palette="RdYlGn", legend=False, ax=ax)
ax.set_title("Avg Delivery Days per Review Score", fontsize=16, fontweight="bold")
ax.set_xlabel("Review Score")
ax.set_ylabel("Avg Delivery Days")
for p in ax.patches:
    ax.text(p.get_x() + p.get_width()/2, p.get_height() + 0.2,
            f"{p.get_height():.1f}", ha="center", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "05_delivery_vs_review.png"))
plt.close()
print("✅ Plot 5 saved: Delivery Days vs Review Score")

# =========================================================
# 6. TOP 10 STATES BY ORDERS
# =========================================================
state_orders = (orders.merge(customers[["customer_id","customer_state"]], on="customer_id")
                       .groupby("customer_state")
                       .size()
                       .sort_values(ascending=False)
                       .head(10)
                       .reset_index(name="num_orders"))

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=state_orders, x="customer_state", y="num_orders",
            hue="customer_state", palette="viridis", legend=False, ax=ax)
ax.set_title("Top 10 States by Number of Orders", fontsize=16, fontweight="bold")
ax.set_xlabel("State")
ax.set_ylabel("Number of Orders")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for p in ax.patches:
    ax.text(p.get_x() + p.get_width()/2, p.get_height() + 50,
            f"{int(p.get_height()):,}", ha="center", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "06_top10_states.png"))
plt.close()
print("✅ Plot 6 saved: Top 10 States by Orders")

# =========================================================
# 7. PAYMENT TYPE DISTRIBUTION
# =========================================================
payment_dist = (payments.groupby("payment_type")["payment_value"]
                         .sum()
                         .sort_values(ascending=False)
                         .reset_index())

fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    payment_dist["payment_value"],
    labels=payment_dist["payment_type"],
    autopct="%1.1f%%",
    colors=["#42A5F5","#66BB6A","#FFA726","#AB47BC"],
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=2)
)
ax.set_title("Payment Type Distribution by Value", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "07_payment_types.png"))
plt.close()
print("✅ Plot 7 saved: Payment Type Distribution")

# =========================================================
# SUMMARY STATS
# =========================================================
total_revenue = order_items["total_price"].sum()
total_orders  = orders["order_id"].nunique()
avg_order_val = total_revenue / total_orders
avg_score     = reviews["review_score"].mean()

print("\n" + "="*45)
print("📊 BUSINESS SUMMARY")
print("="*45)
print(f"Total Orders   : {total_orders:,}")
print(f"Total Revenue  : R$ {total_revenue:,.2f}")
print(f"Avg Order Value: R$ {avg_order_val:,.2f}")
print(f"Avg Review Score: {avg_score:.2f} / 5.0")
print("="*45)
print("\n✅ EDA Complete! Check output/plots/ for all charts.")