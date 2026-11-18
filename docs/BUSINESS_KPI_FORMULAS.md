# Retail Business KPI Formulas & Calculation Engine Specification

**Document Reference:** KPI-SPEC-2026-V1  
**Dataset:** `03_Retail.xlsx`  
**Execution Mode:** Deterministic Python (Pandas/NumPy) & SQL Engine  
**Period:** May 1, 2026 – October 31, 2026  

---

## 1. Principles of Deterministic Analytics

1. **Zero LLM Calculation**: Large Language Models are strictly prohibited from performing raw arithmetic operations on financial datasets. All sums, averages, ratios, and percentages are computed in the Python Service layer (`backend/services/kpi_service.py`).
2. **Order Status Enforcement**:
   - **Realized Revenue & COGS**: Must be computed exclusively on `order_status = 'Completed'`.
   - **Pipeline Leakage**: `Returned` and `Cancelled` orders are analyzed as lost revenue and operational bottlenecks.
3. **Data Availability Guardrail**: If an industry KPI cannot be computed from available columns (e.g., footfall conversion rate), the platform explicitly marks it as `UNSUPPORTED_DATA_BOUNDARY` rather than estimating or hallucinating.

---

## 2. Definitive KPI Catalog & Formulas

### 2.1 Top-Line Revenue & Order Metrics
| KPI Name | Source Table(s) & Column(s) | Mathematical Formula | Verified Dataset Value (May–Oct 2026) |
| :--- | :--- | :--- | :--- |
| **Total Gross Revenue** | `transactions.gross_amount` (`order_status = 'Completed'`) | $$\text{Gross Revenue} = \sum \text{gross\_amount}_{\text{completed}}$$ | ₹114,717,566.35 |
| **Total Discounts** | `transactions.discount` (`order_status = 'Completed'`) | $$\text{Total Discount} = \sum \text{discount}_{\text{completed}}$$ | ₹4,875,456.14 |
| **Total Net Revenue** | `transactions.net_amount` (`order_status = 'Completed'`) | $$\text{Net Revenue} = \sum (\text{gross\_amount} - \text{discount})_{\text{completed}}$$ | ₹109,842,110.21 |
| **Completed Orders** | `transactions.transaction_id` (`order_status = 'Completed'`) | $$\text{Completed Orders} = \text{Count}(\text{transaction\_id}_{\text{completed}})$$ | 1,244 orders |
| **Average Order Value (AOV)** | `transactions.net_amount`, `transactions.transaction_id` | $$\text{AOV} = \frac{\text{Net Revenue}_{\text{completed}}}{\text{Completed Orders}}$$ | ₹88,297.52 |
| **Total Units Sold** | `transaction_items.quantity`, joined with `transactions` | $$\text{Units Sold} = \sum \text{quantity}_{\text{completed}}$$ | 9,332 units |
| **Average Units per Order** | `transaction_items.quantity` / `transactions.transaction_id` | $$\text{Basket Size} = \frac{\text{Units Sold}_{\text{completed}}}{\text{Completed Orders}}$$ | 7.50 units/order (across 2.5 lines/trx) |

### 2.2 Profitability & Cost Metrics
| KPI Name | Source Table(s) & Column(s) | Mathematical Formula | Verified Dataset Value |
| :--- | :--- | :--- | :--- |
| **Cost of Goods Sold (COGS)** | `transaction_items.quantity`, `products.unit_cost` | $$\text{COGS} = \sum (\text{quantity} \times \text{unit\_cost})_{\text{completed}}$$ | ₹85,652,192.94 |
| **Gross Profit** | `Net Revenue`, `COGS` | $$\text{Gross Profit} = \text{Net Revenue} - \text{COGS}$$ | ₹24,189,917.27 |
| **Gross Profit Margin (%)** | `Gross Profit`, `Net Revenue` | $$\text{Gross Margin} = \left(\frac{\text{Gross Profit}}{\text{Net Revenue}}\right) \times 100$$ | 22.02% |
| **Total Operating Expenses (OpEx)** | `expenses.amount` | $$\text{Total OpEx} = \sum \text{amount}$$ | ₹28,107,904.22 |
| **Net Operating Profit (EBIT)** | `Gross Profit`, `Total OpEx` | $$\text{Operating Profit} = \text{Gross Profit} - \text{Total OpEx}$$ | -₹3,917,986.95 (Net Deficit) |
| **Operating Margin (%)** | `Operating Profit`, `Net Revenue` | $$\text{Operating Margin} = \left(\frac{\text{Operating Profit}}{\text{Net Revenue}}\right) \times 100$$ | -3.57% |

### 2.3 Quality, Fulfillment & Pipeline Leakage
| KPI Name | Source Table(s) & Column(s) | Mathematical Formula | Verified Dataset Value |
| :--- | :--- | :--- | :--- |
| **Order Completion Rate** | `transactions.order_status` | $$\text{Completion Rate} = \frac{N_{\text{completed}}}{N_{\text{total}}} \times 100$$ | 49.76% (1,244 / 2,500) |
| **Order Return Rate** | `transactions.order_status` | $$\text{Return Rate} = \frac{N_{\text{returned}}}{N_{\text{total}}} \times 100$$ | 25.80% (645 / 2,500) |
| **Order Cancellation Rate** | `transactions.order_status` | $$\text{Cancellation Rate} = \frac{N_{\text{cancelled}}}{N_{\text{total}}} \times 100$$ | 24.44% (611 / 2,500) |
| **Returned Revenue Lost** | `transactions.net_amount` (`order_status = 'Returned'`) | $$\text{Lost Revenue}_{\text{return}} = \sum \text{net\_amount}_{\text{returned}}$$ | ₹54,540,598.98 |
| **Cancelled Revenue Lost** | `transactions.net_amount` (`order_status = 'Cancelled'`) | $$\text{Lost Revenue}_{\text{cancel}} = \sum \text{net\_amount}_{\text{cancelled}}$$ | ₹51,350,638.75 |

### 2.4 Customer Insights & Retention
| KPI Name | Source Table(s) & Column(s) | Mathematical Formula | Verified Dataset Value |
| :--- | :--- | :--- | :--- |
| **Total Active Customers** | `customers.customer_id`, `transactions.customer_id` | $$\text{Active Customers} = \text{Distinct}(\text{customer\_id in completed trx})$$ | 739 unique customers |
| **Repeat Purchase Rate** | `transactions.customer_id` (`order_status = 'Completed'`) | $$\text{Repeat Rate} = \frac{\text{Customers with } >1 \text{ completed order}}{\text{Total Active Customers}} \times 100$$ | 46.14% (341 / 739) |
| **Customer LTV (Average)** | `Net Revenue` / `Total Active Customers` | $$\text{Avg LTV} = \frac{\text{Net Revenue}}{\text{Active Customers}}$$ | ₹148,636.14 |

### 2.5 Inventory & Warehouse Velocity
| KPI Name | Source Table(s) & Column(s) | Mathematical Formula | Verified Dataset Value |
| :--- | :--- | :--- | :--- |
| **Stockout Risk Count** | `inventory_movements`, `products.reorder_level` | Count of products where $$\text{Net Stock} \le \text{reorder\_level}$$ | Dynamically computed per product |
| **Net Stock Calculation** | `inventory_movements.movement_type`, `quantity` | $$\text{Net Stock} = (\text{Purchase} + \text{Return}) - (\text{Sale} + \text{Transfer}) \pm \text{Adjustment}$$ | 300 Products tracked across 8 Warehouses |
| **Inventory Turnover Ratio** | `COGS`, `Average Inventory Value` | $$\text{Turnover} = \frac{\text{COGS}}{\text{Avg Inventory Valuation}}$$ | Tracked on monthly rolling basis |

---

## 3. Month-over-Month Comparative Formulas

For any metric $M$ in month $t$ vs month $t-1$:
$$\text{MoM Growth \%} = \left(\frac{M_t - M_{t-1}}{M_{t-1}}\right) \times 100$$

### Verified Monthly Metrics Table:
- **May 2026**: ₹15.53M Net Revenue | ₹3.35M Gross Profit | 21.55% Margin | ₹4.85M OpEx
- **June 2026**: ₹16.48M Net Revenue (+6.09%) | ₹3.61M Gross Profit (+7.74%) | 21.88% Margin | ₹4.03M OpEx (-16.77%)
- **July 2026**: ₹18.44M Net Revenue (+11.92%) | ₹4.03M Gross Profit (+11.73%) | 21.85% Margin | ₹4.26M OpEx (+5.70%)
- **August 2026**: ₹20.42M Net Revenue (+10.73%) | ₹4.51M Gross Profit (+11.94%) | 22.08% Margin | ₹4.75M OpEx (+11.33%)
- **September 2026**: ₹17.56M Net Revenue (-14.01%) | ₹3.88M Gross Profit (-13.93%) | 22.10% Margin | ₹4.74M OpEx (-0.19%)
- **October 2026**: ₹21.41M Net Revenue (+21.93%) | ₹4.82M Gross Profit (+24.12%) | 22.50% Margin | ₹5.48M OpEx (+15.69%)
