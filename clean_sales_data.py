
import pandas as pd
from pathlib import Path

# 1. Load the raw dataset
folder = Path(__file__).parent
input_file = folder / "code_orbit_sales_raw.csv"

df = pd.read_csv(input_file)

print("========== RAW DATASET ==========")
print(df.head())
print("\nDataset Shape:", df.shape)

# Record initial data quality
initial_rows = len(df)
missing_before = df.isnull().sum().sum()
duplicates_before = df.duplicated(subset=["order_id"]).sum()

# 2. Remove duplicate orders
df = df.drop_duplicates(subset=["order_id"], keep="first")

# 3. Clean text columns
text_columns = [
    "customer_name", "product", "category",
    "region", "payment_method", "sales_rep",
    "order_status"
]

for col in text_columns:
    df[col] = df[col].astype("string").str.strip()

# Standardize capitalization
for col in ["customer_name", "product", "category",
            "region", "sales_rep", "order_status"]:
    df[col] = df[col].str.title()

# Standardize payment methods
df["payment_method"] = df["payment_method"].str.upper()

payment_map = {
    "UPI": "UPI",
    "CREDIT CARD": "Credit Card",
    "DEBIT CARD": "Debit Card",
    "CASH": "Cash",
    "NET BANKING": "Net Banking"
}

df["payment_method"] = df["payment_method"].replace(payment_map)


# 4. Convert dates without changing ISO-format dates
raw_dates = df["order_date"].astype("string").str.strip()

iso_mask = raw_dates.str.match(
    r"^\d{4}-\d{2}-\d{2}$",
    na=False
)

parsed_dates = pd.Series(
    pd.NaT,
    index=df.index,
    dtype="datetime64[ns]"
)

# Parse YYYY-MM-DD dates correctly
parsed_dates.loc[iso_mask] = pd.to_datetime(
    raw_dates.loc[iso_mask],
    format="%Y-%m-%d",
    errors="coerce"
)

# Parse other formats such as DD-MM-YYYY and Mar 11, 2026
parsed_dates.loc[~iso_mask] = pd.to_datetime(
    raw_dates.loc[~iso_mask],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

df["order_date"] = parsed_dates


# 5. Convert numeric columns
df["quantity"] = pd.to_numeric(
    df["quantity"], errors="coerce"
)

df["unit_price"] = (
    df["unit_price"]
    .astype("string")
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)

df["unit_price"] = pd.to_numeric(
    df["unit_price"], errors="coerce"
)

df["discount_pct"] = pd.to_numeric(
    df["discount_pct"], errors="coerce"
)

# 6. Handle missing values
for col in ["customer_name", "product", "category",
            "region", "payment_method", "sales_rep",
            "order_status"]:
    if df[col].isnull().any():
        df[col] = df[col].fillna(df[col].mode()[0])

for col in ["quantity", "unit_price", "discount_pct"]:
    df[col] = df[col].fillna(df[col].median())

if df["order_date"].isnull().any():
    df["order_date"] = df["order_date"].fillna(
        df["order_date"].mode()[0]
    )

# 7. Calculate total sales after discount
df["total_sales"] = (
    df["quantity"] * df["unit_price"]
    * (1 - df["discount_pct"] / 100)
).round(2)

# 8. Format the date consistently
df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

# 9. Check the cleaned dataset
missing_after = df.isnull().sum().sum()
duplicates_after = df.duplicated(subset=["order_id"]).sum()

# 10. Export cleaned dataset
output_file = folder / "cleaned_sales_data.csv"
df.to_csv(output_file, index=False)

# 11. Create cleaning documentation
report = f"""
CODE ORBIT INTERNSHIP
TASK 1: DATA CLEANING REPORT

Initial number of rows: {initial_rows}
Final number of rows: {len(df)}

Duplicate orders removed: {duplicates_before}

Missing values before cleaning: {missing_before}
Missing values after cleaning: {missing_after}

Duplicate orders after cleaning: {duplicates_after}

CLEANING OPERATIONS:
1. Loaded the raw CSV dataset using Pandas.
2. Removed duplicate order records.
3. Removed unnecessary spaces from text columns.
4. Standardized text capitalization.
5. Standardized payment method names.
6. Converted mixed date formats into YYYY-MM-DD.
7. Converted quantity and price columns into numeric values.
8. Removed currency symbols and commas from prices.
9. Handled missing values using mode and median.
10. Calculated total sales after discount.
11. Exported the cleaned dataset into a new CSV file.

OUTPUT FILE: cleaned_sales_data.csv
"""

report_file = folder / "cleaning_report.txt"
report_file.write_text(report, encoding="utf-8")

print("\n========== CLEANING SUMMARY ==========")
print("Initial rows:", initial_rows)
print("Final rows:", len(df))
print("Duplicates removed:", duplicates_before)
print("Missing values before:", missing_before)
print("Missing values after:", missing_after)
print("Duplicates remaining:", duplicates_after)

print("\n========== CLEANED DATASET ==========")
print(df.head())

print("\nCleaned dataset saved successfully!")
print("Report saved successfully!")
