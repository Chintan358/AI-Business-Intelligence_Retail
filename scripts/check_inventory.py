import pandas as pd

excel_path = "data/03_Retail.xlsx"
inv = pd.read_excel(excel_path, sheet_name="Inventory_Movements")
prods = pd.read_excel(excel_path, sheet_name="Products")

print("Inventory movement quantity stats:")
print(inv.groupby('movement_type')['quantity'].describe())

# Check negative quantities
print("Any negative quantity in inventory:", (inv['quantity'] < 0).sum())

# Net stock by product: if Purchase (+), Return (+), Sale (-), Transfer (-/internal), Adjustment (+/-)?
# Or let's see how inventory movements relates to products reorder_level
print("\nProduct reorder levels summary:")
print(prods['reorder_level'].describe())
