import pandas as pd

# LOAD DATA
customers = pd.read_csv("../1_raw_data/customer.csv")
orders = pd.read_csv("../1_raw_data/orders.csv")
products = pd.read_csv("../1_raw_data/products.csv")
order_items = pd.read_csv("../1_raw_data/order_items.csv")

print("Customers:", customers.shape)
print("Orders:", orders.shape)
print("Order Items:", order_items.shape)
print("Products:", products.shape)

# INITIAL DATA CHECK 
print("\nCustomers Info")
print(customers.info())

print("\nOrders Info")
print(orders.info())

print("\nOrder Items Info")
print(order_items.info())

print("\nProducts Info")
print(products.info())

# Missing values
print("\nMissing values in customers:\n", customers.isnull().sum())
print("\nMissing values in orders:\n", orders.isnull().sum())
print("\nMissing values in order_items:\n", order_items.isnull().sum())
print("\nMissing values in products:\n", products.isnull().sum())

# Duplicate checks
print("\nDuplicate rows:")
print("Customers:", customers.duplicated().sum())
print("Orders:", orders.duplicated().sum())
print("Order Items:", order_items.duplicated().sum())
print("Products:", products.duplicated().sum())

# DATA TYPE CONVERSION
customers["customer_id"] = customers["customer_id"].astype(str)
orders["customer_id"] = orders["customer_id"].astype(str)
order_items["product_id"] = order_items["product_id"].astype(str)
products["product_id"] = products["product_id"].astype(str)

customers["signup_date"] = pd.to_datetime(customers["signup_date"], errors="coerce")
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
orders["order_ts"] = pd.to_datetime(orders["order_ts"], errors="coerce")

# DATA CLEANING 
# Fill Missing 
# full_name using first + last name 
mask_missing_fullname = customers["full_name"].isna() | (customers["full_name"].str.strip() == "")
customers.loc[mask_missing_fullname, "full_name"] = (
    customers.loc[mask_missing_fullname, "first_name"].fillna("") + " " +
    customers.loc[mask_missing_fullname, "last_name"].fillna("")
).str.strip()

# Fill missing state using city mapping
city_state_map = orders.dropna(subset=["state"]).drop_duplicates("city")[["city", "state"]]
city_state_dict = dict(zip(city_state_map["city"], city_state_map["state"]))
orders["state"] = orders["state"].fillna(orders["city"].map(city_state_dict))

customers["age"] = customers["age"].fillna(customers["age"].median())
order_items["discount"] = order_items["discount"].fillna(0)
products["mrp"] = products["mrp"].fillna(products["mrp"].median())

# Replace empty names with "Unknown"
customers.loc[customers["full_name"].str.strip() == "", "full_name"] = "Unknown"
customers["gender"] = customers["gender"].fillna("Unknown")
customers["city"] = customers["city"].fillna("Unknown")
orders["city"] = orders["city"].fillna("Unknown")
orders["state"] = orders["state"].fillna("Unknown")
orders["payment_method"] = orders["payment_method"].fillna("Unknown")
orders["order_status"] = orders["order_status"].fillna("Unknown")
products["brand"] = products["brand"].fillna("Unknown")
products["category"] = products["category"].fillna("Unknown")
products["sub_category"] = products["sub_category"].fillna("Unknown")

# Drop unnecessary columns
customers = customers.drop(columns=["first_name", "last_name"])

# DATA VALIDATION 
missing_products = order_items[~order_items["product_id"].isin(products["product_id"])]
print("Order items with missing products:", len(missing_products))

# Remove unmatched product records
order_items = order_items[
    order_items["product_id"].isin(products["product_id"])
]

print("Order items after cleaning:", len(order_items))

# MERGE DATA 
sales = orders.merge(order_items, on="order_id", how="inner")
sales = sales.merge(products, on="product_id", how="left")
sales = sales.merge(customers, on="customer_id", how="left", suffixes=("_order", "_customer"))

print("Final merged sales shape:", sales.shape)

# FEATURE ENGINEERING 
sales["gross_amount"] = sales["quantity"] * sales["unit_price"]
sales["revenue"] = sales["net_amount"]

sales["discount_pct"] = ((sales["discount"] / sales["gross_amount"]).fillna(0)) * 100

sales["order_year"] = sales["order_date"].dt.year
sales["order_month"] = sales["order_date"].dt.month
sales["order_day"] = sales["order_date"].dt.day

sales["year_month"] = sales["order_date"].dt.to_period("M").astype(str)
sales["order_weekday"] = sales["order_date"].dt.day_name()

# AGGREGATIONS 
monthly_sales = sales.groupby("year_month").agg(
    total_revenue=("revenue", "sum"),
    total_orders=("order_id", "nunique"),
    total_customers=("customer_id", "nunique"),
    total_quantity=("quantity", "sum")
).reset_index()

category_performance = sales.groupby("category").agg(
    revenue=("revenue", "sum"),
    total_orders=("order_id", "nunique"),
    quantity_sold=("quantity", "sum")
).reset_index().sort_values(by="revenue", ascending=False)

city_sales = sales.groupby("city_customer").agg(
    revenue=("revenue", "sum"),
    total_orders=("order_id", "nunique"),
    customers=("customer_id", "nunique")
).reset_index().sort_values(by="revenue", ascending=False)

customer_clv = sales.groupby("customer_id").agg(
    total_revenue=("revenue", "sum"),
    total_orders=("order_id", "nunique"),
    total_quantity=("quantity", "sum")
).reset_index().sort_values(by="total_revenue", ascending=False)

payment_analysis = sales.groupby("payment_method").agg(
    revenue=("revenue", "sum"),
    total_orders=("order_id", "nunique")
).reset_index().sort_values(by="revenue", ascending=False)

#  9. SAVE OUTPUT 
sales.to_csv("../cleaned_data/sales_fact_table.csv", index=False)
monthly_sales.to_csv("../cleaned_data/monthly_sales.csv", index=False)
category_performance.to_csv("../cleaned_data/category_performance.csv", index=False)
city_sales.to_csv("../cleaned_data/city_sales.csv", index=False)
customer_clv.to_csv("../cleaned_data/customer_clv.csv", index=False)
payment_analysis.to_csv("../cleaned_data/payment_analysis.csv", index=False)