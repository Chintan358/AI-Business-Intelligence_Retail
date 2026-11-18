import pandas as pd

excel_path = "data/03_Retail.xlsx"
customers = pd.read_excel(excel_path, sheet_name="Customers")
products = pd.read_excel(excel_path, sheet_name="Products")
transactions = pd.read_excel(excel_path, sheet_name="Transactions")
transaction_items = pd.read_excel(excel_path, sheet_name="Transaction_Items")
inventory = pd.read_excel(excel_path, sheet_name="Inventory_Movements")
expenses = pd.read_excel(excel_path, sheet_name="Expenses")

print("--- Categorical Values ---")
print("Customer segments:", customers['customer_segment'].value_counts().to_dict())
print("Cities:", customers['city'].value_counts().to_dict())
print("Product categories:", products['category'].value_counts().to_dict())
print("Transaction order statuses:", transactions['order_status'].value_counts().to_dict())
print("Channels:", transactions['channel'].value_counts().to_dict())
print("Payment methods:", transactions['payment_method'].value_counts().to_dict())
print("Inventory movement types:", inventory['movement_type'].value_counts().to_dict())
print("Expense categories:", expenses['category'].value_counts().to_dict())

print("\n--- Financial & Operational Checks ---")
# Check completed vs cancelled vs returned transactions
print("Total transactions:", len(transactions))
print("Transactions by status:")
for status, group in transactions.groupby('order_status'):
    print(f"  {status}: {len(group)} trx, Gross: {group['gross_amount'].sum():,.2f}, Discount: {group['discount'].sum():,.2f}, Net: {group['net_amount'].sum():,.2f}")

# Join transaction items with products to inspect COGS and profit
merged_items = transaction_items.merge(products, on="product_id", suffixes=('_item', '_prod'))
merged_items = merged_items.merge(transactions[['transaction_id', 'transaction_date', 'order_status']], on="transaction_id")
merged_items['cogs'] = merged_items['quantity'] * merged_items['unit_cost']
completed_items = merged_items[merged_items['order_status'] == 'Completed']

print(f"\nCompleted Line Items: {len(completed_items)}")
print(f"Total Completed Items Line Total: {completed_items['line_total'].sum():,.2f}")
print(f"Total Completed Items COGS: {completed_items['cogs'].sum():,.2f}")
print(f"Gross Profit from Completed Items: {(completed_items['line_total'].sum() - completed_items['cogs'].sum()):,.2f}")

total_expenses = expenses['amount'].sum()
print(f"\nTotal Operating Expenses: {total_expenses:,.2f}")

# Monthly breakdown of completed transactions
transactions['month'] = pd.to_datetime(transactions['transaction_date']).dt.to_period('M')
expenses['month'] = pd.to_datetime(expenses['expense_date']).dt.to_period('M')

monthly_rev = transactions[transactions['order_status'] == 'Completed'].groupby('month')['net_amount'].sum()
monthly_exp = expenses.groupby('month')['amount'].sum()
print("\n--- Monthly Financials (Completed Sales vs Expenses) ---")
monthly_df = pd.DataFrame({'Net Revenue': monthly_rev, 'Expenses': monthly_exp})
print(monthly_df)

print("\n--- Foreign Key Integrity ---")
missing_customers = set(transactions['customer_id']) - set(customers['customer_id'])
print(f"Missing customer_ids in transactions: {len(missing_customers)}")
missing_products_in_items = set(transaction_items['product_id']) - set(products['product_id'])
print(f"Missing product_ids in transaction_items: {len(missing_products_in_items)}")
missing_trx_in_items = set(transaction_items['transaction_id']) - set(transactions['transaction_id'])
print(f"Missing transaction_ids in transaction_items: {len(missing_trx_in_items)}")
missing_products_in_inv = set(inventory['product_id']) - set(products['product_id'])
print(f"Missing product_ids in inventory: {len(missing_products_in_inv)}")
