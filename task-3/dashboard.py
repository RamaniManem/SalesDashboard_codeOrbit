
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# CODE ORBIT INTERNSHIP
# TASK 3: INTERACTIVE SALES DASHBOARD
# ==========================================

# Page configuration
st.set_page_config(
    page_title="Code Orbit Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Dashboard title
st.title("📊 Sales Performance Dashboard")
st.caption("Code Orbit Internship | Task 3 - Dashboard Creation")

# Load dataset
folder = Path(__file__).parent
file_path = folder.parent / "cleaned_sales_data.csv"


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)

    data["order_date"] = pd.to_datetime(
        data["order_date"], errors="coerce"
    )

    data["quantity"] = pd.to_numeric(
        data["quantity"], errors="coerce"
    )

    data["unit_price"] = pd.to_numeric(
        data["unit_price"], errors="coerce"
    )

    data["total_sales"] = pd.to_numeric(
        data["total_sales"], errors="coerce"
    )

    data["discount_pct"] = pd.to_numeric(
        data["discount_pct"], errors="coerce"
    )

    return data


try:
    df = load_data(file_path)

except FileNotFoundError:
    st.error(
        "Dataset not found. Please place "
        "cleaned_sales_data.csv in the same folder "
        "as dashboard.py."
    )
    st.stop()


# Sidebar filters
st.sidebar.header("🔎 Dashboard Filters")

regions = sorted(df["region"].dropna().unique())
categories = sorted(df["category"].dropna().unique())
statuses = sorted(df["order_status"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Select Region",
    regions,
    default=regions
)

selected_categories = st.sidebar.multiselect(
    "Select Category",
    categories,
    default=categories
)

selected_statuses = st.sidebar.multiselect(
    "Select Order Status",
    statuses,
    default=["Completed"]
)

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply filters
filtered_df = df[
    (df["region"].isin(selected_regions))
    & (df["category"].isin(selected_categories))
    & (df["order_status"].isin(selected_statuses))
].copy()

# Date filter
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["order_date"].dt.date >= start_date)
        & (filtered_df["order_date"].dt.date <= end_date)
    ]

# Completed orders are used for revenue metrics
completed_df = filtered_df[
    filtered_df["order_status"].str.lower() == "completed"
].copy()

# Calculate KPI metrics
total_revenue = completed_df["total_sales"].sum()

total_orders = completed_df["order_id"].nunique()

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0 else 0
)

total_units = completed_df["quantity"].sum()

# KPI cards
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"₹{total_revenue:,.2f}"
)

col2.metric(
    "Completed Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Average Order Value",
    f"₹{average_order_value:,.2f}"
)

col4.metric(
    "Units Sold",
    f"{total_units:,.0f}"
)

st.divider()

# Show order status summary
st.subheader("Order Status Overview")

status_summary = (
    filtered_df.groupby("order_status")
    .agg(
        orders=("order_id", "nunique"),
        sales_value=("total_sales", "sum")
    )
    .reset_index()
)

status_col1, status_col2 = st.columns(2)

with status_col1:
    status_chart = px.pie(
        status_summary,
        names="order_status",
        values="orders",
        title="Orders by Status",
        hole=0.45
    )

    st.plotly_chart(
        status_chart,
        use_container_width=True
    )

with status_col2:
    status_bar = px.bar(
        status_summary,
        x="order_status",
        y="orders",
        title="Order Status Count",
        labels={
            "order_status": "Order Status",
            "orders": "Number of Orders"
        },
        text="orders"
    )

    st.plotly_chart(
        status_bar,
        use_container_width=True
    )

st.divider()

# Monthly sales trend
st.subheader("📈 Monthly Sales Trend")

if not completed_df.empty:
    completed_df["month"] = (
        completed_df["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_sales = (
        completed_df.groupby("month")
        .agg(
            revenue=("total_sales", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
        .sort_values("month")
    )

    monthly_chart = px.line(
        monthly_sales,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue",
        labels={
            "month": "Month",
            "revenue": "Revenue (₹)"
        }
    )

    st.plotly_chart(
        monthly_chart,
        use_container_width=True
    )

else:
    st.info("No completed sales available for the selected filters.")

st.divider()

# Product and category charts
st.subheader("🛍️ Product and Category Performance")

product_col, category_col = st.columns(2)

with product_col:
    if not completed_df.empty:
        product_sales = (
            completed_df.groupby("product")
            ["total_sales"].sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        product_chart = px.bar(
            product_sales,
            x="total_sales",
            y="product",
            orientation="h",
            title="Revenue by Product",
            labels={
                "total_sales": "Revenue (₹)",
                "product": "Product"
            }
        )

        product_chart.update_layout(
            yaxis={"categoryorder": "total ascending"}
        )

        st.plotly_chart(
            product_chart,
            use_container_width=True
        )

with category_col:
    if not completed_df.empty:
        category_sales = (
            completed_df.groupby("category")
            ["total_sales"].sum()
            .reset_index()
        )

        category_chart = px.pie(
            category_sales,
            names="category",
            values="total_sales",
            title="Revenue by Category",
            hole=0.4
        )

        st.plotly_chart(
            category_chart,
            use_container_width=True
        )

st.divider()

# Regional sales analysis
st.subheader("🌍 Regional Sales Performance")

if not completed_df.empty:
    region_sales = (
        completed_df.groupby("region")
        ["total_sales"].sum()
        .reset_index()
        .sort_values("total_sales", ascending=False)
    )

    region_chart = px.bar(
        region_sales,
        x="region",
        y="total_sales",
        title="Revenue by Region",
        labels={
            "region": "Region",
            "total_sales": "Revenue (₹)"
        },
        text_auto=".2s"
    )

    st.plotly_chart(
        region_chart,
        use_container_width=True
    )

st.divider()

# Detailed sales table
st.subheader("📋 Detailed Sales Data")

st.write(
    "Use the filters in the sidebar to explore "
    "different sales records."
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# Download filtered dataset
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Sales Data",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)

# Footer
st.divider()

st.caption(
    "Developed using Python, Pandas, Streamlit "
    "and Plotly | Code Orbit Internship"
)
