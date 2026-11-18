import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_and_health():
    res1 = client.get("/")
    assert res1.status_code == 200
    assert "status" in res1.json()

    res2 = client.get("/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "healthy"

def test_auth_login():
    res = client.post("/api/v1/auth/login", data={"username": "admin@retailbi.com", "password": "Admin@123456"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    return data["access_token"]

def test_kpi_endpoints_authenticated():
    token = test_auth_login()
    headers = {"Authorization": f"Bearer {token}"}

    res_kpi = client.get("/api/v1/kpis/summary", headers=headers)
    assert res_kpi.status_code == 200
    assert res_kpi.json()["completed_orders"] == 1244

    res_monthly = client.get("/api/v1/kpis/monthly", headers=headers)
    assert res_monthly.status_code == 200
    assert len(res_monthly.json()) == 6

    res_categories = client.get("/api/v1/kpis/categories", headers=headers)
    assert res_categories.status_code == 200
    assert len(res_categories.json()) == 4

    res_alerts = client.get("/api/v1/kpis/stockout-alerts", headers=headers)
    assert res_alerts.status_code == 200
    assert len(res_alerts.json()) > 0

def test_admin_overview():
    token = test_auth_login()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/admin/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["transactions_count"] == 2500
    assert data["customers_count"] == 1200
    assert data["products_count"] == 300
