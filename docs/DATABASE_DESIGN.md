# Database Design Specification

**Document Reference:** DBD-RET-2026-V1  
**Target RDBMS:** PostgreSQL (Live Hosted on Render)  
**ORM:** SQLAlchemy 2.0  
**Migration Tool:** Alembic  
**Data Integrity:** Foreign Key Constraints, Unique Constraints, B-Tree Indexes  

---

## 1. Schema Design Principles

1. **Third Normal Form (3NF) Compliance**: All retail transaction items, products, categories, stores, and customers are normalized without transitive dependencies.
2. **Deterministic Data Separation**: Retail entity records (`customers`, `products`, `transactions`, `transaction_items`, `inventory_movements`, `expenses`) are maintained in immutable ledger tables.
3. **Multi-Tenant System Isolation**: System records (`users`, `business_profiles`, `analysis_sessions`, `agent_logs`, `strategic_recommendations`, `approval_requests`, `chat_conversations`, `chat_messages`) are strictly tied to authenticated user accounts via `user_id`.
4. **Auditability**: Every consequential recommendation, managerial approval, agent log, and file upload has high-precision timestamps (`created_at`, `updated_at`, `decision_date`).

---

## 2. Table Specifications

### 2.1 Retail Business Tables

#### `customers`
```sql
CREATE TABLE customers (
    customer_id VARCHAR(16) PRIMARY KEY,
    customer_name VARCHAR(128) NOT NULL,
    city VARCHAR(64) NOT NULL,
    signup_date DATE NOT NULL,
    customer_segment VARCHAR(32) NOT NULL, -- Regular, New, Wholesale, Premium
    email VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_customers_segment ON customers(customer_segment);
```

#### `products`
```sql
CREATE TABLE products (
    product_id VARCHAR(16) PRIMARY KEY,
    product_name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL, -- Grocery, Electronics, Home, Fashion
    unit_price NUMERIC(12, 2) NOT NULL,
    unit_cost NUMERIC(12, 2) NOT NULL,
    reorder_level INTEGER NOT NULL,
    supplier_id VARCHAR(16) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_supplier ON products(supplier_id);
```

#### `transactions`
```sql
CREATE TABLE transactions (
    transaction_id VARCHAR(16) PRIMARY KEY,
    customer_id VARCHAR(16) NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    transaction_date DATE NOT NULL,
    store_id VARCHAR(16) NOT NULL,
    channel VARCHAR(32) NOT NULL, -- In-store, Mobile App, Online
    gross_amount NUMERIC(14, 2) NOT NULL,
    discount NUMERIC(14, 2) DEFAULT 0.00,
    net_amount NUMERIC(14, 2) NOT NULL,
    payment_method VARCHAR(32) NOT NULL, -- Card, UPI, Cash, Wallet
    order_status VARCHAR(32) NOT NULL, -- Completed, Returned, Cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_status ON transactions(order_status);
CREATE INDEX idx_transactions_store ON transactions(store_id);
CREATE INDEX idx_transactions_channel ON transactions(channel);
```

#### `transaction_items`
```sql
CREATE TABLE transaction_items (
    line_item_id VARCHAR(16) PRIMARY KEY,
    transaction_id VARCHAR(16) NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    product_id VARCHAR(16) NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL,
    line_total NUMERIC(14, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_items_transaction ON transaction_items(transaction_id);
CREATE INDEX idx_items_product ON transaction_items(product_id);
```

#### `inventory_movements`
```sql
CREATE TABLE inventory_movements (
    movement_id VARCHAR(16) PRIMARY KEY,
    product_id VARCHAR(16) NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    movement_date DATE NOT NULL,
    movement_type VARCHAR(32) NOT NULL, -- Adjustment, Return, Purchase, Transfer, Sale
    quantity INTEGER NOT NULL,
    warehouse_id VARCHAR(16) NOT NULL,
    reference_no VARCHAR(32) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_inv_product ON inventory_movements(product_id);
CREATE INDEX idx_inv_warehouse ON inventory_movements(warehouse_id);
CREATE INDEX idx_inv_date ON inventory_movements(movement_date);
```

#### `expenses`
```sql
CREATE TABLE expenses (
    expense_id VARCHAR(16) PRIMARY KEY,
    expense_date DATE NOT NULL,
    store_id VARCHAR(16) NOT NULL,
    category VARCHAR(64) NOT NULL, -- Marketing, Rent, Staff Salary, Logistics, Packaging, Utilities
    amount NUMERIC(14, 2) NOT NULL CHECK (amount >= 0),
    vendor VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_store ON expenses(store_id);
```

---

### 2.2 Application, Multi-Agent & Governance Tables

#### `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(128) UNIQUE NOT NULL,
    hashed_password VARCHAR(256) NOT NULL,
    full_name VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'manager', -- admin, manager, analyst
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### `business_profiles`
```sql
CREATE TABLE business_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(128) NOT NULL,
    industry VARCHAR(64) NOT NULL DEFAULT 'Retail',
    team_size VARCHAR(32),
    target_margin NUMERIC(5, 2) DEFAULT 25.00,
    business_goals TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### `uploaded_datasets`
```sql
CREATE TABLE uploaded_datasets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    filename VARCHAR(256) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    total_records INTEGER NOT NULL,
    sheet_details JSONB,
    status VARCHAR(32) NOT NULL DEFAULT 'Completed', -- Processing, Completed, Failed
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### `analysis_sessions`
```sql
CREATE TABLE analysis_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    dataset_id INTEGER REFERENCES uploaded_datasets(id) ON DELETE SET NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'Pending', -- Pending, Running, Completed, Verified, Failed
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_duration_sec NUMERIC(10, 2),
    executive_summary TEXT,
    consolidated_plan JSONB,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_scorecard JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### `agent_logs`
```sql
CREATE TABLE agent_logs (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    agent_name VARCHAR(64) NOT NULL,
    agent_role VARCHAR(128) NOT NULL,
    task_name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL, -- Running, Completed, Failed
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_duration_sec NUMERIC(10, 2),
    output_text TEXT,
    structured_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_agent_logs_session ON agent_logs(session_id);
```

#### `strategic_recommendations`
```sql
CREATE TABLE strategic_recommendations (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    title VARCHAR(256) NOT NULL,
    category VARCHAR(64) NOT NULL, -- Marketing, Finance, Operations, Strategy
    description TEXT NOT NULL,
    expected_roi VARCHAR(128),
    risk_level VARCHAR(32) DEFAULT 'Medium', -- Low, Medium, High
    supporting_evidence JSONB,
    status VARCHAR(32) NOT NULL DEFAULT 'Pending', -- Pending, Approved, Rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### `approval_requests`
```sql
CREATE TABLE approval_requests (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER NOT NULL REFERENCES strategic_recommendations(id) ON DELETE CASCADE,
    requested_by_agent VARCHAR(64) NOT NULL,
    reviewed_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    decision VARCHAR(32) NOT NULL DEFAULT 'Pending', -- Pending, Approved, Rejected
    manager_comments TEXT,
    decision_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### `generated_reports`
```sql
CREATE TABLE generated_reports (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES analysis_sessions(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(64) NOT NULL, -- Consolidated, DataAnalyst, Marketing, Finance, Operations, Strategy, Verification
    title VARCHAR(256) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size_bytes INTEGER,
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### `chat_conversations` & `chat_messages`
```sql
CREATE TABLE chat_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(256) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,
    sender VARCHAR(16) NOT NULL, -- user, assistant
    message TEXT NOT NULL,
    grounding_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
