import os
import sqlite3
from contextlib import closing

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import Counter, CONTENT_TYPE_LATEST, generate_latest

DB_PATH = os.getenv("DB_PATH", "orders.db")

app = FastAPI(title="Order Service")

# Prometheus metrics
REQUESTS = Counter("http_requests_total", "HTTP requests received", ["path"])
ORDERS_CREATED = Counter("orders_created_total", "Orders created")


class OrderIn(BaseModel):
    customer: str
    product: str
    quantity: int


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   customer TEXT NOT NULL,
                   product TEXT NOT NULL,
                   quantity INTEGER NOT NULL)"""
        )
        conn.commit()


init_db()


@app.get("/health")
def health():
    REQUESTS.labels("/health").inc()
    return {"status": "ok"}


@app.post("/orders", status_code=201)
def create_order(order: OrderIn):
    REQUESTS.labels("/orders").inc()
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be greater than 0")
    with closing(get_conn()) as conn:
        cur = conn.execute(
            "INSERT INTO orders (customer, product, quantity) VALUES (?, ?, ?)",
            (order.customer, order.product, order.quantity),
        )
        conn.commit()
        new_id = cur.lastrowid
    ORDERS_CREATED.inc()
    return {"id": new_id, **order.model_dump()}


@app.get("/orders")
def list_orders():
    REQUESTS.labels("/orders").inc()
    with closing(get_conn()) as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    REQUESTS.labels("/orders/{id}").inc()
    with closing(get_conn()) as conn:
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    return dict(row)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
