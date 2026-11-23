
import pandas as pd
from pathlib import Path

# ==========================================
# CODE ORBIT INTERNSHIP
# TASK 2: SALES DATA ANALYSIS WITH PANDAS
# ==========================================

# 1. Load cleaned dataset

folder = Path(__file__).parent

# Task-1 cleaned dataset is one folder above Task-2
input_file = folder.parent / "cleaned_sales_data.csv"

df = pd.read_csv(input_file)


df = pd.read_csv(input_file)

print("========== SALES DATASET ==========")
print(df.head())
print("\nDataset Shape:", df.shape)

# 2. Convert columns to correct data types
df["order_date"] = pd.to_datetime(
    df["order_date"], errors="coerce"
)

df["quantity"] = pd.to_numeric(
    df["quantity"], errors="coerce"
)

df["unit_price"] = pd.to_numeric(
    df["unit_price"], errors="coerce"
)

df["total_sales"] = pd.to_numeric(
    df["total_sales"], errors="coerce"
)

# 3. Separate orders by status
completed = df[
    df["order_status"].str.lower() == "completed"
].copy()

pending = df[
    df["order_status"].str.lower() == "pending"
].copy()

cancelled = df[
    df["order_status"].str.lower() == "cancelled"
].copy()

# 4. Calculate key sales metrics
total_revenue = completed["total_sales"].sum()

total_completed_orders = completed["order_id"].nunique()

average_order_value = (
    total_revenue / total_completed_orders
    if total_completed_orders > 0 else 0
)

total_units_sold = completed["quantity"].sum()

total_pending_orders = pending["order_id"].nunique()

total_cancelled_orders = cancelled["order_id"].nunique()

# 5. Product-wise sales analysis
product_sales = (
    completed.groupby("product")
    .agg(
        units_sold=("quantity", "sum"),
        total_revenue=("total_sales", "sum"),
        number_of_orders=("order_id", "nunique")
    )
    .sort_values("total_revenue", ascending=False)
    .reset_index()
)

top_product = (
    product_sales.iloc[0]["product"]
    if not product_sales.empty else "No data"
)

# 6. Category-wise sales analysis
category_sales = (
    completed.groupby("category")
    .agg(
        total_revenue=("total_sales", "sum"),
        units_sold=("quantity", "sum"),
        number_of_orders=("order_id", "nunique")
    )
    .sort_values("total_revenue", ascending=False)
    .reset_index()
)

# 7. Region-wise sales analysis
region_sales = (
    completed.groupby("region")
    .agg(
        total_revenue=("total_sales", "sum"),
        units_sold=("quantity", "sum"),
        number_of_orders=("order_id", "nunique")
    )
    .sort_values("total_revenue", ascending=False)
    .reset_index()
)

# 8. Monthly sales analysis
completed["month"] = completed["order_date"].dt.to_period("M").astype(str)

monthly_sales = (
    completed.groupby("month")
    .agg(
        total_revenue=("total_sales", "sum"),
        units_sold=("quantity", "sum"),
        number_of_orders=("order_id", "nunique")
    )
    .reset_index()
    .sort_values("month")
)

# 9. Save analysis tables
product_sales.to_csv(
    folder / "product_sales_analysis.csv", index=False
)

category_sales.to_csv(
    folder / "category_sales_analysis.csv", index=False
)

region_sales.to_csv(
    folder / "region_sales_analysis.csv", index=False
)

monthly_sales.to_csv(
    folder / "monthly_sales_analysis.csv", index=False
)

# 10. Display results
print("\n========== KEY SALES METRICS ==========")
print(f"Total Revenue: ₹{total_revenue:,.2f}")
print(f"Completed Orders: {total_completed_orders}")
print(f"Average Order Value: ₹{average_order_value:,.2f}")
print(f"Total Units Sold: {total_units_sold}")
print(f"Pending Orders: {total_pending_orders}")
print(f"Cancelled Orders: {total_cancelled_orders}")

print("\n========== TOP PRODUCTS ==========")
print(product_sales.head(5).to_string(index=False))

print("\n========== CATEGORY-WISE SALES ==========")
print(category_sales.to_string(index=False))

print("\n========== REGION-WISE SALES ==========")
print(region_sales.to_string(index=False))

print("\n========== MONTHLY SALES ==========")
print(monthly_sales.to_string(index=False))

# 11. Create short sales report
report = f"""
CODE ORBIT INTERNSHIP
TASK 2: SALES DATA ANALYSIS REPORT

1. DATASET OVERVIEW
Total records analyzed: {len(df)}
Completed orders: {total_completed_orders}
Pending orders: {total_pending_orders}
Cancelled orders: {total_cancelled_orders}

2. KEY SALES METRICS
Total revenue from completed orders: ₹{total_revenue:,.2f}
Average order value: ₹{average_order_value:,.2f}
Total units sold: {total_units_sold}

3. TOP-PERFORMING PRODUCT
Top product by revenue: {top_product}

4. CATEGORY-WISE ANALYSIS
{category_sales.to_string(index=False)}

5. REGION-WISE ANALYSIS
{region_sales.to_string(index=False)}

6. MONTHLY SALES ANALYSIS
{monthly_sales.to_string(index=False)}

7. CONCLUSION
The sales dataset was analyzed using Pandas.
Revenue, average order value, product performance,
category performance, regional performance and monthly
sales trends were calculated.

Cancelled orders were excluded from revenue calculations.
Pending and cancelled orders were reported separately.

The analysis helps identify strong-performing products,
categories and regions for business decision-making.
"""

report_file = folder / "sales_analysis_report.txt"

report_file.write_text(
    report, encoding="utf-8"
)

print("\nSales analysis completed successfully!")
print("Analysis tables and report have been saved.")
