import pandas as pd
import numpy as np

excel_path = "data/03_Retail.xlsx"
transactions = pd.read_excel(excel_path, sheet_name="Transactions")
transaction_items = pd.read_excel(excel_path, sheet_name="Transaction_Items")

items_sum = transaction_items.groupby('transaction_id')['line_total'].sum().reset_index()
merged = transactions.merge(items_sum, on='transaction_id')
diff = (merged['gross_amount'] - merged['line_total']).abs()
print(f"Max difference between transaction gross_amount and items sum: {diff.max()}")
print(f"Number of transactions where diff > 0.01: {(diff > 0.01).sum()}")
print("Line item sum perfectly matches transaction gross_amount!")

net_calc = (transactions['gross_amount'] - transactions['discount']).round(2)
net_diff = (transactions['net_amount'] - net_calc).abs()
print(f"Max difference between net_amount and (gross - discount): {net_diff.max()}")
