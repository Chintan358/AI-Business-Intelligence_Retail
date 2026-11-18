from sqlalchemy import Column, String, Integer, Float, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(16), primary_key=True, index=True)
    customer_name = Column(String(128), nullable=False)
    city = Column(String(64), nullable=False, index=True)
    signup_date = Column(Date, nullable=False)
    customer_segment = Column(String(32), nullable=False, index=True)  # Regular, New, Wholesale, Premium
    email = Column(String(128), nullable=False, unique=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="customer")

class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(16), primary_key=True, index=True)
    product_name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False, index=True)  # Grocery, Electronics, Home, Fashion
    unit_price = Column(Numeric(12, 2), nullable=False)
    unit_cost = Column(Numeric(12, 2), nullable=False)
    reorder_level = Column(Integer, nullable=False)
    supplier_id = Column(String(16), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction_items = relationship("TransactionItem", back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product")

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(16), primary_key=True, index=True)
    customer_id = Column(String(16), ForeignKey("customers.customer_id"), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    store_id = Column(String(16), nullable=False, index=True)
    channel = Column(String(32), nullable=False, index=True)  # In-store, Mobile App, Online
    gross_amount = Column(Numeric(14, 2), nullable=False)
    discount = Column(Numeric(14, 2), default=0.0)
    net_amount = Column(Numeric(14, 2), nullable=False)
    payment_method = Column(String(32), nullable=False)  # Card, UPI, Cash, Wallet
    order_status = Column(String(32), nullable=False, index=True)  # Completed, Returned, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")

class TransactionItem(Base):
    __tablename__ = "transaction_items"

    line_item_id = Column(String(16), primary_key=True, index=True)
    transaction_id = Column(String(16), ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    product_id = Column(String(16), ForeignKey("products.product_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(14, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    movement_id = Column(String(16), primary_key=True, index=True)
    product_id = Column(String(16), ForeignKey("products.product_id"), nullable=False, index=True)
    movement_date = Column(Date, nullable=False, index=True)
    movement_type = Column(String(32), nullable=False)  # Adjustment, Return, Purchase, Transfer, Sale
    quantity = Column(Integer, nullable=False)
    warehouse_id = Column(String(16), nullable=False, index=True)
    reference_no = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory_movements")

class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(String(16), primary_key=True, index=True)
    expense_date = Column(Date, nullable=False, index=True)
    store_id = Column(String(16), nullable=False, index=True)
    category = Column(String(64), nullable=False, index=True)  # Marketing, Rent, Staff Salary, Logistics, Packaging, Utilities
    amount = Column(Numeric(14, 2), nullable=False)
    vendor = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
