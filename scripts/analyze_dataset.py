import openpyxl
import pandas as pd
import json

excel_path = "data/03_Retail.xlsx"
wb = openpyxl.load_workbook(excel_path, read_only=True)
sheet_names = wb.sheetnames
print(f"Sheet names ({len(sheet_names)}): {sheet_names}")

summary = {}
for sheet in sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet)
    print(f"\n{'='*50}\nSHEET: {sheet}\n{'='*50}")
    print(f"Shape: {df.shape}")
    print("Columns & Dtypes:")
    for col, dtype in df.dtypes.items():
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        print(f"  - {col} ({dtype}): {null_count} nulls, {unique_count} unique. Example: {df[col].dropna().iloc[0] if len(df[col].dropna())>0 else 'None'}")
    
    # Check date columns if any
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    for dc in date_cols:
        parsed_dates = pd.to_datetime(df[dc], errors='coerce')
        print(f"  * Date range for {dc}: {parsed_dates.min()} to {parsed_dates.max()}")

    summary[sheet] = {
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": {c: str(d) for c, d in df.dtypes.items()},
        "null_counts": {c: int(df[c].isnull().sum()) for c in df.columns},
        "sample": df.head(2).to_dict(orient="records")
    }

with open("data/dataset_summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\nSummary saved to data/dataset_summary.json")
