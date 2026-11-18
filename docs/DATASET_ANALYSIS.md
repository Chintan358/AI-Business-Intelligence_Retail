# Dataset Analysis & Validation Report

**Dataset:** `03_Retail.xlsx`  
**Industry:** Retail – Sales & Inventory Intelligence  
**Coverage Period:** May 1, 2026 – October 31, 2026 (Exactly 6 months / 184 days)  
**Total Sheets:** 7 (`Customers`, `Products`, `Transactions`, `Transaction_Items`, `Inventory_Movements`, `Expenses`, `README`)  

---

## 1. Sheet Summaries & Structural Profiles

### 1.1 Sheet: `Customers`
- **Row Count:** 1,200 records
- **Primary Key:** `customer_id` (Unique, non-null, format `CUS00001` - `CUS01200`)
- **Columns:**
  - `customer_id` (String): Unique identifier
  - `customer_name` (String): Full customer name (298 distinct names)
  - `city` (String): 10 distinct Indian metro/tier-2 cities: Surat (130), Mumbai (130), Rajkot (129), Gandhinagar (122), Vadodara (120), Anand (120), Nadiad (118), Pune (116), Ahmedabad (111), Bharuch (104).
  - `signup_date` (Date): Spans 2026-05-01 to 2026-10-31
  - `customer_segment` (String): 4 distinct tiers: Regular (325, 27.1%), New (302, 25.2%), Wholesale (292, 24.3%), Premium (281, 23.4%).
  - `email` (String): Unique contact email addresses.
- **Null Values:** 0
- **Duplicates:** 0 duplicate IDs

### 1.2 Sheet: `Products`
- **Row Count:** 300 records
- **Primary Key:** `product_id` (Unique, non-null, format `PRD0001` - `PRD0300`)
- **Columns:**
  - `product_id` (String): Unique product code
  - `product_name` (String): Product descriptor (e.g., Bedsheet 001, Smart Watch 004, Dry Fruits 003)
  - `category` (String): 4 core retail departments: Grocery (81, 27.0%), Electronics (76, 25.3%), Home (72, 24.0%), Fashion (71, 23.7%).
  - `unit_price` (Float): Retail catalog selling price (Range: ₹190.98 to ₹24,911.47; Mean: ₹12,796.84)
  - `unit_cost` (Float): Supplier acquisition cost (Range: ₹139.95 to ₹17,999.86; Mean: ₹9,072.82)
  - `reorder_level` (Integer): Safety threshold for stock replenishment (Range: 10 to 80 units; Mean: 43.57)
  - `supplier_id` (String): 79 unique supplier references (`SUP001` - `SUP080`)
- **Null Values:** 0
- **Duplicates:** 0 duplicate IDs

### 1.3 Sheet: `Transactions`
- **Row Count:** 2,500 records
- **Primary Key:** `transaction_id` (Unique, non-null, format `TRX00001` - `TRX02500`)
- **Foreign Key:** `customer_id` -> `Customers.customer_id` (100% matched, 0 orphaned keys)
- **Columns:**
  - `transaction_id` (String): Primary transaction identifier
  - `customer_id` (String): Customer foreign key
  - `transaction_date` (Date): Dates from 2026-05-01 to 2026-10-31
  - `store_id` (String): 15 unique physical / virtual store locations (`STR01` - `STR15`)
  - `channel` (String): 3 shopping channels: In-store (867, 34.7%), Mobile App (826, 33.0%), Online (807, 32.3%)
  - `gross_amount` (Float): Total before discount (Sum: ₹225,230,294.04)
  - `discount` (Float): Total promotional concession (Sum: ₹9,496,946.10)
  - `net_amount` (Float): Payable amount = `gross_amount` - `discount` (Sum: ₹215,733,347.94)
  - `payment_method` (String): 4 settlement methods: Wallet (632, 25.3%), Card (629, 25.2%), UPI (622, 24.9%), Cash (617, 24.7%)
  - `order_status` (String): 3 fulfillment states:
    - **Completed:** 1,244 orders (49.8%) | Gross: ₹114,717,566.35 | Discount: ₹4,875,456.14 | Net: ₹109,842,110.21
    - **Returned:** 645 orders (25.8%) | Gross: ₹56,972,475.23 | Discount: ₹2,431,876.25 | Net: ₹54,540,598.98
    - **Cancelled:** 611 orders (24.4%) | Gross: ₹53,540,252.46 | Discount: ₹2,189,613.71 | Net: ₹51,350,638.75

### 1.4 Sheet: `Transaction_Items`
- **Row Count:** 6,269 records
- **Primary Key:** `line_item_id` (Unique, non-null, format `LIN000001` - `LIN006269`)
- **Foreign Keys:**
  - `transaction_id` -> `Transactions.transaction_id` (100% integrity)
  - `product_id` -> `Products.product_id` (100% integrity)
- **Columns:**
  - `line_item_id` (String): Unique basket line identifier
  - `transaction_id` (String): Transaction reference
  - `product_id` (String): Product reference
  - `quantity` (Integer): Basket quantity per line (Range: 1 to 5 units; Mean: 2.99)
  - `unit_price` (Float): Unit price matching catalog price
  - `line_total` (Float): `quantity` * `unit_price` (Sum across all items: ₹225,230,294.04)
- **Verification Result:** The sum of `line_total` across lines grouped by `transaction_id` equals `Transactions.gross_amount` with maximum discrepancy < 1e-10.

### 1.5 Sheet: `Inventory_Movements`
- **Row Count:** 1,800 records
- **Primary Key:** `movement_id` (Unique, non-null, format `MOV00001` - `MOV01800`)
- **Foreign Key:** `product_id` -> `Products.product_id` (100% integrity)
- **Columns:**
  - `movement_id` (String): Unique stock log identifier
  - `product_id` (String): Product reference
  - `movement_date` (Date): 2026-05-01 to 2026-10-31
  - `movement_type` (String): 5 event types:
    - `Adjustment`: 384 movements (21.3%)
    - `Return`: 370 movements (20.6%)
    - `Purchase`: 365 movements (20.3%)
    - `Transfer`: 347 movements (19.3%)
    - `Sale`: 334 movements (18.6%)
  - `quantity` (Integer): Unit count (1 to 150 units per record)
  - `warehouse_id` (String): 8 fulfillment hubs (`WH01` - `WH08`)
  - `reference_no` (String): Audit tracking reference (`REF000001` - `REF001800`)

### 1.6 Sheet: `Expenses`
- **Row Count:** 600 records
- **Primary Key:** `expense_id` (Unique, non-null, format `REX0001` - `REX0600`)
- **Foreign Key:** `store_id` -> Store identifier (`STR01` - `STR15`)
- **Columns:**
  - `expense_id` (String): Unique expense voucher code
  - `expense_date` (Date): 2026-05-01 to 2026-10-31
  - `store_id` (String): Store facility reference
  - `category` (String): 6 operating categories:
    - Marketing: 112 vouchers (₹5,317,824.16)
    - Rent: 110 vouchers (₹5,234,912.80)
    - Staff Salary: 100 vouchers (₹4,812,450.92)
    - Logistics: 98 vouchers (₹4,452,190.23)
    - Packaging: 97 vouchers (₹4,378,910.15)
    - Utilities: 83 vouchers (₹3,911,615.96)
  - `amount` (Float): Expense in INR (Total: ₹28,107,904.22)
  - `vendor` (String): 100 unique vendors (`Vendor 001` - `Vendor 100`)

---

## 2. Mathematical Integrity & Verified Benchmarks

### 2.1 Sales & Profitability Ground Truth (Completed Orders Only)
- **Completed Orders:** 1,244
- **Completed Gross Revenue:** ₹114,717,566.35
- **Completed Total Discounts:** ₹4,875,456.14
- **Completed Net Revenue:** ₹109,842,110.21
- **Cost of Goods Sold (COGS):** ₹85,652,192.94
- **Gross Profit:** ₹24,189,917.27 (Net Revenue - COGS)
- **Gross Profit Margin:** 22.02%
- **Total Operating Expenses (OpEx):** ₹28,107,904.22
- **Net Operating Profit (EBIT):** -₹3,917,986.95 (Operating deficit due to high cancellation & return rates)
- **Average Order Value (AOV):** ₹88,297.52

### 2.2 Monthly Revenue & Expense Timeline
| Month | Completed Orders | Net Revenue (₹) | COGS (₹) | Gross Profit (₹) | OpEx (₹) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **2026-05** | 185 | 15,531,889.18 | 12,185,210.40 | 3,346,678.78 | 4,846,355.07 |
| **2026-06** | 192 | 16,477,629.50 | 12,871,940.15 | 3,605,689.35 | 4,033,616.68 |
| **2026-07** | 207 | 18,441,535.12 | 14,412,890.30 | 4,028,644.82 | 4,263,317.49 |
| **2026-08** | 225 | 20,419,952.36 | 15,910,230.12 | 4,509,722.24 | 4,746,316.43 |
| **2026-09** | 201 | 17,559,830.81 | 13,678,410.50 | 3,881,420.31 | 4,737,530.12 |
| **2026-10** | 234 | 21,411,273.24 | 16,593,511.47 | 4,817,761.77 | 5,480,768.43 |
| **Total** | **1,244** | **109,842,110.21** | **85,652,192.94** | **24,189,917.27** | **28,107,904.22** |

---

## 3. Identifiable Business Issues & Anomaly Flags

1. **High Return & Cancellation Rates**:
   - Out of 2,500 total orders, only 1,244 were completed (49.76%).
   - Returned: 645 orders (25.80%), amounting to ₹54.54M net loss in potential revenue.
   - Cancelled: 611 orders (24.44%), representing ₹51.35M in pipeline abandonment.
   - *Combined non-realization rate is 50.24%* – a critical operational vulnerability.
2. **Negative Net Operating Margin**:
   - Total Gross Profit is ₹24.19M, but total Store Operating Expenses reach ₹28.11M.
   - The business experiences an operating loss of ₹3.92M over the 6-month period, driven heavily by marketing (₹5.32M) and rent (₹5.23M) overheads that fail to convert due to the 50% cancellation/return leakage.
3. **September Performance Dip**:
   - Net revenue dropped from ₹20.42M in August to ₹17.56M in September (-14.0%), before recovering to ₹21.41M in October (+21.9%).
4. **Channel Variance**:
   - In-store: 34.7% of volume, Mobile App: 33.0%, Online: 32.3%. Return rates are notably higher on digital channels (Online and Mobile App).

---

## 4. Dataset Boundaries & Non-Calculable Metrics (No Hallucination Policy)

The following metrics **cannot** be computed from the dataset and will **never** be fabricated:
- **Customer Acquisition Cost (CAC) per Channel**: Marketing expenses are tracked by store (`store_id`), not by digital campaign or marketing channel.
- **Website Traffic / Conversion Rate**: No clickstream, session, or bounce rate logs exist.
- **Product Reviews / NPS / CSAT**: No customer sentiment or rating columns exist.
- **Real-time GPS Tracking / Carrier Delivery Times**: Only warehouse inventory movement records exist; transit durations between warehouses and customers are unrecorded.
