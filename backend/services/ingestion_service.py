import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import (
    Customer,
    Product,
    Transaction,
    TransactionItem,
    InventoryMovement,
    Expense,
    User,
    BusinessProfile,
    UploadedDataset
)
from backend.config import settings

def seed_database_from_excel(db: Session, excel_path: str = None) -> dict:
    if excel_path is None:
        excel_path = settings.DEFAULT_DATASET_PATH

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel dataset not found at {excel_path}")

    # Check if data is already seeded
    existing_trx_count = db.query(Transaction).count()
    if existing_trx_count > 0:
        return {
            "status": "already_seeded",
            "message": f"Database already contains {existing_trx_count} transactions.",
            "transactions": existing_trx_count,
            "customers": db.query(Customer).count(),
            "products": db.query(Product).count(),
            "items": db.query(TransactionItem).count(),
            "inventory": db.query(InventoryMovement).count(),
            "expenses": db.query(Expense).count()
        }

    print(f"Loading Excel file from {excel_path}...")
    xls = pd.ExcelFile(excel_path)
    
    # 1. Ingest Customers
    df_customers = pd.read_excel(xls, "Customers")
    customers = []
    for _, row in df_customers.iterrows():
        signup_dt = pd.to_datetime(row["signup_date"]).date()
        c = Customer(
            customer_id=str(row["customer_id"]).strip(),
            customer_name=str(row["customer_name"]).strip(),
            city=str(row["city"]).strip(),
            signup_date=signup_dt,
            customer_segment=str(row["customer_segment"]).strip(),
            email=str(row["email"]).strip()
        )
        customers.append(c)
    db.bulk_save_objects(customers)
    db.commit()
    print(f"Inserted {len(customers)} customers.")

    # 2. Ingest Products
    df_products = pd.read_excel(xls, "Products")
    products = []
    for _, row in df_products.iterrows():
        p = Product(
            product_id=str(row["product_id"]).strip(),
            product_name=str(row["product_name"]).strip(),
            category=str(row["category"]).strip(),
            unit_price=float(row["unit_price"]),
            unit_cost=float(row["unit_cost"]),
            reorder_level=int(row["reorder_level"]),
            supplier_id=str(row["supplier_id"]).strip()
        )
        products.append(p)
    db.bulk_save_objects(products)
    db.commit()
    print(f"Inserted {len(products)} products.")

    # 3. Ingest Transactions
    df_trx = pd.read_excel(xls, "Transactions")
    transactions = []
    for _, row in df_trx.iterrows():
        t_dt = pd.to_datetime(row["transaction_date"]).date()
        t = Transaction(
            transaction_id=str(row["transaction_id"]).strip(),
            customer_id=str(row["customer_id"]).strip(),
            transaction_date=t_dt,
            store_id=str(row["store_id"]).strip(),
            channel=str(row["channel"]).strip(),
            gross_amount=float(row["gross_amount"]),
            discount=float(row["discount"]),
            net_amount=float(row["net_amount"]),
            payment_method=str(row["payment_method"]).strip(),
            order_status=str(row["order_status"]).strip()
        )
        transactions.append(t)
    db.bulk_save_objects(transactions)
    db.commit()
    print(f"Inserted {len(transactions)} transactions.")

    # 4. Ingest Transaction Items
    df_items = pd.read_excel(xls, "Transaction_Items")
    items = []
    for _, row in df_items.iterrows():
        item = TransactionItem(
            line_item_id=str(row["line_item_id"]).strip(),
            transaction_id=str(row["transaction_id"]).strip(),
            product_id=str(row["product_id"]).strip(),
            quantity=int(row["quantity"]),
            unit_price=float(row["unit_price"]),
            line_total=float(row["line_total"])
        )
        items.append(item)
    db.bulk_save_objects(items)
    db.commit()
    print(f"Inserted {len(items)} transaction items.")

    # 5. Ingest Inventory Movements
    df_inv = pd.read_excel(xls, "Inventory_Movements")
    movements = []
    for _, row in df_inv.iterrows():
        m_dt = pd.to_datetime(row["movement_date"]).date()
        m = InventoryMovement(
            movement_id=str(row["movement_id"]).strip(),
            product_id=str(row["product_id"]).strip(),
            movement_date=m_dt,
            movement_type=str(row["movement_type"]).strip(),
            quantity=int(row["quantity"]),
            warehouse_id=str(row["warehouse_id"]).strip(),
            reference_no=str(row["reference_no"]).strip()
        )
        movements.append(m)
    db.bulk_save_objects(movements)
    db.commit()
    print(f"Inserted {len(movements)} inventory movements.")

    # 6. Ingest Expenses
    df_exp = pd.read_excel(xls, "Expenses")
    expenses = []
    for _, row in df_exp.iterrows():
        e_dt = pd.to_datetime(row["expense_date"]).date()
        e = Expense(
            expense_id=str(row["expense_id"]).strip(),
            expense_date=e_dt,
            store_id=str(row["store_id"]).strip(),
            category=str(row["category"]).strip(),
            amount=float(row["amount"]),
            vendor=str(row["vendor"]).strip()
        )
        expenses.append(e)
    db.bulk_save_objects(expenses)
    db.commit()
    print(f"Inserted {len(expenses)} expenses.")

    # Register initial dataset record
    dataset_record = UploadedDataset(
        filename=os.path.basename(excel_path),
        file_size_bytes=os.path.getsize(excel_path),
        total_records=len(transactions) + len(items) + len(movements) + len(expenses),
        sheet_details={
            "Customers": len(customers),
            "Products": len(products),
            "Transactions": len(transactions),
            "Transaction_Items": len(items),
            "Inventory_Movements": len(movements),
            "Expenses": len(expenses)
        },
        status="Completed"
    )
    db.add(dataset_record)
    db.commit()

    return {
        "status": "success",
        "customers": len(customers),
        "products": len(products),
        "transactions": len(transactions),
        "items": len(items),
        "inventory": len(movements),
        "expenses": len(expenses)
    }
