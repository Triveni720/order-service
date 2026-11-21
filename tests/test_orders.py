import os

# Use a separate database for tests (set BEFORE importing the app)
TEST_DB = "test_orders.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["DB_PATH"] = TEST_DB

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_order():
    new = {"customer": "Ravi", "product": "Laptop", "quantity": 2}
    created = client.post("/orders", json=new)
    assert created.status_code == 201
    order_id = created.json()["id"]

    fetched = client.get(f"/orders/{order_id}")
    assert fetched.status_code == 200
    assert fetched.json()["product"] == "Laptop"


def test_invalid_quantity_is_rejected():
    bad = {"customer": "Ravi", "product": "Pen", "quantity": 0}
    assert client.post("/orders", json=bad).status_code == 400


def test_missing_order_returns_404():
    assert client.get("/orders/99999").status_code == 404


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "orders_created_total" in response.text
