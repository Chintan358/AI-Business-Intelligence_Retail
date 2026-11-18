import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List

class KPIService:
    def __init__(self, db: Session):
        self.db = db

    def get_raw_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Loads normalized SQL records into pandas DataFrames for deterministic analytical computation."""
        conn = self.db.connection()
        customers_df = pd.read_sql("SELECT * FROM customers", conn)
        products_df = pd.read_sql("SELECT * FROM products", conn)
        transactions_df = pd.read_sql("SELECT * FROM transactions", conn)
        items_df = pd.read_sql("SELECT * FROM transaction_items", conn)
        inv_df = pd.read_sql("SELECT * FROM inventory_movements", conn)
        expenses_df = pd.read_sql("SELECT * FROM expenses", conn)

        # Ensure correct date parsing
        customers_df['signup_date'] = pd.to_datetime(customers_df['signup_date'])
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        inv_df['movement_date'] = pd.to_datetime(inv_df['movement_date'])
        expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date'])

        # Numeric conversions
        for col in ['unit_price', 'unit_cost']:
            products_df[col] = pd.to_numeric(products_df[col], errors='coerce')
        for col in ['gross_amount', 'discount', 'net_amount']:
            transactions_df[col] = pd.to_numeric(transactions_df[col], errors='coerce')
        for col in ['unit_price', 'line_total']:
            items_df[col] = pd.to_numeric(items_df[col], errors='coerce')
        expenses_df['amount'] = pd.to_numeric(expenses_df['amount'], errors='coerce')

        return {
            "customers": customers_df,
            "products": products_df,
            "transactions": transactions_df,
            "items": items_df,
            "inventory": inv_df,
            "expenses": expenses_df
        }

    def get_executive_kpis(self) -> Dict[str, Any]:
        """Computes verified core retail KPIs strictly according to standard formulas."""
        dfs = self.get_raw_dataframes()
        tx = dfs["transactions"]
        items = dfs["items"]
        products = dfs["products"]
        expenses = dfs["expenses"]

        total_orders = len(tx)
        completed_tx = tx[tx["order_status"] == "Completed"]
        returned_tx = tx[tx["order_status"] == "Returned"]
        cancelled_tx = tx[tx["order_status"] == "Cancelled"]

        completed_count = len(completed_tx)
        returned_count = len(returned_tx)
        cancelled_count = len(cancelled_tx)

        gross_revenue = float(completed_tx["gross_amount"].sum())
        discount_amount = float(completed_tx["discount"].sum())
        net_revenue = float(completed_tx["net_amount"].sum())

        # Returned & Cancelled Lost Revenue
        returned_revenue_lost = float(returned_tx["net_amount"].sum())
        cancelled_revenue_lost = float(cancelled_tx["net_amount"].sum())

        # Average Order Value (AOV)
        aov = round(net_revenue / completed_count, 2) if completed_count > 0 else 0.0

        # Join items with products for COGS
        completed_ids = set(completed_tx["transaction_id"])
        completed_items = items[items["transaction_id"].isin(completed_ids)]
        items_with_cost = completed_items.merge(products[["product_id", "unit_cost"]], on="product_id")
        
        cogs = float((items_with_cost["quantity"] * items_with_cost["unit_cost"]).sum())
        total_units_sold = int(completed_items["quantity"].sum())
        gross_profit = round(net_revenue - cogs, 2)
        gross_profit_margin_pct = round((gross_profit / net_revenue * 100), 2) if net_revenue > 0 else 0.0

        total_opex = float(expenses["amount"].sum())
        operating_profit = round(gross_profit - total_opex, 2)
        operating_margin_pct = round((operating_profit / net_revenue * 100), 2) if net_revenue > 0 else 0.0

        # Customer Retention & Repeat Purchase
        customer_completed_orders = completed_tx.groupby("customer_id")["transaction_id"].count()
        active_customers = len(customer_completed_orders)
        repeat_customers = int((customer_completed_orders > 1).sum())
        repeat_purchase_rate_pct = round((repeat_customers / active_customers * 100), 2) if active_customers > 0 else 0.0

        # Inventory Low Stock count
        net_stock_df = self.get_product_stock_health(dfs["inventory"], products)
        stockout_risk_count = int((net_stock_df["current_stock"] <= net_stock_df["reorder_level"]).sum())

        return {
            "period": "May 1, 2026 – October 31, 2026",
            "total_transactions": total_orders,
            "completed_orders": completed_count,
            "returned_orders": returned_count,
            "cancelled_orders": cancelled_count,
            "order_completion_rate_pct": round(completed_count / total_orders * 100, 2),
            "order_return_rate_pct": round(returned_count / total_orders * 100, 2),
            "order_cancellation_rate_pct": round(cancelled_count / total_orders * 100, 2),
            "gross_revenue": round(gross_revenue, 2),
            "discount_amount": round(discount_amount, 2),
            "net_revenue": round(net_revenue, 2),
            "returned_revenue_lost": round(returned_revenue_lost, 2),
            "cancelled_revenue_lost": round(cancelled_revenue_lost, 2),
            "aov": aov,
            "total_units_sold": total_units_sold,
            "avg_units_per_order": round(total_units_sold / completed_count, 2) if completed_count > 0 else 0.0,
            "cogs": round(cogs, 2),
            "gross_profit": gross_profit,
            "gross_profit_margin_pct": gross_profit_margin_pct,
            "total_operating_expenses": round(total_opex, 2),
            "net_operating_profit": operating_profit,
            "operating_margin_pct": operating_margin_pct,
            "active_customers": active_customers,
            "repeat_customers": repeat_customers,
            "repeat_purchase_rate_pct": repeat_purchase_rate_pct,
            "stockout_risk_count": stockout_risk_count
        }

    def get_monthly_metrics(self) -> List[Dict[str, Any]]:
        """Returns monthly MoM financial analysis for May through October 2026."""
        dfs = self.get_raw_dataframes()
        tx = dfs["transactions"].copy()
        items = dfs["items"].copy()
        products = dfs["products"].copy()
        expenses = dfs["expenses"].copy()

        tx["month"] = tx["transaction_date"].dt.strftime("%Y-%m")
        expenses["month"] = expenses["expense_date"].dt.strftime("%Y-%m")

        completed_tx = tx[tx["order_status"] == "Completed"]
        
        # Monthly revenues
        monthly_rev = completed_tx.groupby("month").agg(
            gross_revenue=("gross_amount", "sum"),
            discounts=("discount", "sum"),
            net_revenue=("net_amount", "sum"),
            completed_orders=("transaction_id", "count")
        ).reset_index()

        # Monthly COGS
        merged_items = items.merge(tx[["transaction_id", "month", "order_status"]], on="transaction_id")
        merged_items = merged_items[merged_items["order_status"] == "Completed"]
        merged_items = merged_items.merge(products[["product_id", "unit_cost"]], on="product_id")
        merged_items["cogs"] = merged_items["quantity"] * merged_items["unit_cost"]
        monthly_cogs = merged_items.groupby("month")["cogs"].sum().reset_index()

        # Monthly Expenses
        monthly_exp = expenses.groupby("month")["amount"].sum().reset_index()
        monthly_exp.rename(columns={"amount": "operating_expenses"}, inplace=True)

        # Merge monthly
        merged_m = monthly_rev.merge(monthly_cogs, on="month", how="left")
        merged_m = merged_m.merge(monthly_exp, on="month", how="left").fillna(0)

        merged_m["gross_profit"] = merged_m["net_revenue"] - merged_m["cogs"]
        merged_m["gross_margin_pct"] = (merged_m["gross_profit"] / merged_m["net_revenue"] * 100).round(2)
        merged_m["net_operating_profit"] = merged_m["gross_profit"] - merged_m["operating_expenses"]
        merged_m["operating_margin_pct"] = (merged_m["net_operating_profit"] / merged_m["net_revenue"] * 100).round(2)
        merged_m["aov"] = (merged_m["net_revenue"] / merged_m["completed_orders"]).round(2)

        # Month-over-Month growth
        merged_m["revenue_mom_growth_pct"] = merged_m["net_revenue"].pct_change() * 100
        merged_m["revenue_mom_growth_pct"] = merged_m["revenue_mom_growth_pct"].fillna(0).round(2)

        records = merged_m.to_dict(orient="records")
        for r in records:
            for k in ["gross_revenue", "discounts", "net_revenue", "cogs", "operating_expenses", "gross_profit", "net_operating_profit"]:
                r[k] = round(float(r[k]), 2)
        return records

    def get_category_performance(self) -> List[Dict[str, Any]]:
        """Computes department-wise performance metrics (Grocery, Electronics, Home, Fashion)."""
        dfs = self.get_raw_dataframes()
        tx = dfs["transactions"]
        items = dfs["items"]
        products = dfs["products"]

        completed_tx = tx[tx["order_status"] == "Completed"]
        merged = items.merge(completed_tx[["transaction_id"]], on="transaction_id")
        merged = merged.merge(products, on="product_id")
        merged["cogs"] = merged["quantity"] * merged["unit_cost"]
        merged["profit"] = merged["line_total"] - merged["cogs"]

        cat_summary = merged.groupby("category").agg(
            total_revenue=("line_total", "sum"),
            total_units_sold=("quantity", "sum"),
            total_cogs=("cogs", "sum"),
            gross_profit=("profit", "sum")
        ).reset_index()

        cat_summary["gross_margin_pct"] = (cat_summary["gross_profit"] / cat_summary["total_revenue"] * 100).round(2)
        total_rev = cat_summary["total_revenue"].sum()
        cat_summary["revenue_share_pct"] = (cat_summary["total_revenue"] / total_rev * 100).round(2)

        records = cat_summary.to_dict(orient="records")
        for r in records:
            for k in ["total_revenue", "total_cogs", "gross_profit"]:
                r[k] = round(float(r[k]), 2)
        return records

    def get_channel_performance(self) -> List[Dict[str, Any]]:
        """Computes channel metrics across In-store, Mobile App, and Online."""
        dfs = self.get_raw_dataframes()
        tx = dfs["transactions"]

        channel_summary = tx.groupby("channel").agg(
            total_orders=("transaction_id", "count"),
            completed_orders=("order_status", lambda s: (s == "Completed").sum()),
            returned_orders=("order_status", lambda s: (s == "Returned").sum()),
            cancelled_orders=("order_status", lambda s: (s == "Cancelled").sum()),
            total_gross=("gross_amount", "sum"),
            completed_net_revenue=("net_amount", lambda n: n[tx.loc[n.index, "order_status"] == "Completed"].sum()),
            returned_lost_revenue=("net_amount", lambda n: n[tx.loc[n.index, "order_status"] == "Returned"].sum())
        ).reset_index()

        channel_summary["return_rate_pct"] = (channel_summary["returned_orders"] / channel_summary["total_orders"] * 100).round(2)
        channel_summary["cancellation_rate_pct"] = (channel_summary["cancelled_orders"] / channel_summary["total_orders"] * 100).round(2)
        channel_summary["completion_rate_pct"] = (channel_summary["completed_orders"] / channel_summary["total_orders"] * 100).round(2)

        records = channel_summary.to_dict(orient="records")
        for r in records:
            for k in ["total_gross", "completed_net_revenue", "returned_lost_revenue"]:
                r[k] = round(float(r[k]), 2)
        return records

    def get_store_performance(self) -> List[Dict[str, Any]]:
        """Store-by-store sales, allocated operating expenses, and contribution margin."""
        dfs = self.get_raw_dataframes()
        tx = dfs["transactions"]
        expenses = dfs["expenses"]
        items = dfs["items"]
        products = dfs["products"]

        completed_tx = tx[tx["order_status"] == "Completed"]
        store_sales = completed_tx.groupby("store_id").agg(
            completed_orders=("transaction_id", "count"),
            net_revenue=("net_amount", "sum")
        ).reset_index()

        # Store COGS
        merged_items = items.merge(completed_tx[["transaction_id", "store_id"]], on="transaction_id")
        merged_items = merged_items.merge(products[["product_id", "unit_cost"]], on="product_id")
        merged_items["cogs"] = merged_items["quantity"] * merged_items["unit_cost"]
        store_cogs = merged_items.groupby("store_id")["cogs"].sum().reset_index()

        # Store expenses
        store_exp = expenses.groupby("store_id")["amount"].sum().reset_index()
        store_exp.rename(columns={"amount": "operating_expenses"}, inplace=True)

        summary = store_sales.merge(store_cogs, on="store_id", how="left")
        summary = summary.merge(store_exp, on="store_id", how="left").fillna(0)

        summary["gross_profit"] = summary["net_revenue"] - summary["cogs"]
        summary["gross_margin_pct"] = (summary["gross_profit"] / summary["net_revenue"] * 100).round(2)
        summary["net_operating_profit"] = summary["gross_profit"] - summary["operating_expenses"]
        summary["operating_margin_pct"] = (summary["net_operating_profit"] / summary["net_revenue"] * 100).round(2)

        summary.sort_values(by="net_revenue", ascending=False, inplace=True)
        records = summary.to_dict(orient="records")
        for r in records:
            for k in ["net_revenue", "cogs", "operating_expenses", "gross_profit", "net_operating_profit"]:
                r[k] = round(float(r[k]), 2)
        return records

    def get_customer_segment_insights(self) -> List[Dict[str, Any]]:
        """Analyzes buyer tiers (Regular, New, Wholesale, Premium)."""
        dfs = self.get_raw_dataframes()
        customers = dfs["customers"]
        tx = dfs["transactions"]

        completed_tx = tx[tx["order_status"] == "Completed"]
        merged = completed_tx.merge(customers[["customer_id", "customer_segment"]], on="customer_id")

        summary = merged.groupby("customer_segment").agg(
            completed_orders=("transaction_id", "count"),
            unique_customers=("customer_id", "nunique"),
            net_revenue=("net_amount", "sum")
        ).reset_index()

        summary["aov"] = (summary["net_revenue"] / summary["completed_orders"]).round(2)
        total_rev = summary["net_revenue"].sum()
        summary["revenue_share_pct"] = (summary["net_revenue"] / total_rev * 100).round(2)

        records = summary.to_dict(orient="records")
        for r in records:
            r["net_revenue"] = round(float(r["net_revenue"]), 2)
        return records

    def get_product_stock_health(self, inv_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
        """Deterministic stock recalculation: (Purchases + Returns) - (Sales + Transfers) +/- Adjustments."""
        def calc_net(row):
            m_type = row["movement_type"]
            q = row["quantity"]
            if m_type in ["Purchase", "Return"]:
                return q
            elif m_type in ["Sale", "Transfer"]:
                return -q
            else:  # Adjustment
                return q  # Treated as net inventory adjustment

        inv_df = inv_df.copy()
        inv_df["net_delta"] = inv_df.apply(calc_net, axis=1)
        net_stock = inv_df.groupby("product_id")["net_delta"].sum().reset_index()
        net_stock.rename(columns={"net_delta": "current_stock"}, inplace=True)

        merged = products_df.merge(net_stock, on="product_id", how="left")
        merged["current_stock"] = merged["current_stock"].fillna(0).astype(int)
        merged["stockout_risk"] = merged["current_stock"] <= merged["reorder_level"]
        return merged

    def get_stockout_alerts(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Returns products with current inventory at or below safety reorder levels."""
        dfs = self.get_raw_dataframes()
        stock_df = self.get_product_stock_health(dfs["inventory"], dfs["products"])
        risks = stock_df[stock_df["stockout_risk"] == True].copy()
        risks["deficit"] = risks["reorder_level"] - risks["current_stock"]
        risks.sort_values(by="deficit", ascending=False, inplace=True)
        records = risks.head(limit)[["product_id", "product_name", "category", "unit_price", "unit_cost", "current_stock", "reorder_level", "deficit", "supplier_id"]].to_dict(orient="records")
        for r in records:
            r["unit_price"] = round(float(r["unit_price"]), 2)
            r["unit_cost"] = round(float(r["unit_cost"]), 2)
        return records

    def get_top_selling_and_slow_moving_products(self, limit: int = 10) -> Dict[str, Any]:
        """Identifies top-revenue and slow-moving SKUs."""
        dfs = self.get_raw_dataframes()
        tx = dfs["transactions"]
        items = dfs["items"]
        products = dfs["products"]

        completed_tx = tx[tx["order_status"] == "Completed"]
        merged = items.merge(completed_tx[["transaction_id"]], on="transaction_id")
        prod_sales = merged.groupby("product_id").agg(
            units_sold=("quantity", "sum"),
            revenue_generated=("line_total", "sum")
        ).reset_index()

        all_prods = products.merge(prod_sales, on="product_id", how="left")
        all_prods["units_sold"] = all_prods["units_sold"].fillna(0).astype(int)
        all_prods["revenue_generated"] = all_prods["revenue_generated"].fillna(0).round(2)

        # Top selling by revenue
        top_selling = all_prods.sort_values(by="revenue_generated", ascending=False).head(limit)[
            ["product_id", "product_name", "category", "unit_price", "units_sold", "revenue_generated"]
        ].to_dict(orient="records")

        # Slow moving
        slow_moving = all_prods.sort_values(by="units_sold", ascending=True).head(limit)[
            ["product_id", "product_name", "category", "unit_price", "units_sold", "revenue_generated"]
        ].to_dict(orient="records")

        return {
            "top_selling_products": top_selling,
            "slow_moving_products": slow_moving
        }
