# Order Service

![CI](https://github.com/Triveni720/order-service/actions/workflows/ci.yml/badge.svg)

A containerised Python microservice for creating and viewing orders. Built to practise the full delivery lifecycle: API development, SQL storage, automated tests, Docker, CI/CD, Kubernetes and monitoring.

## Tech stack

Python, FastAPI, SQLite (SQL), pytest, Docker, GitHub Actions, Kubernetes (kind), Prometheus

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /health | Health check used by Kubernetes probes |
| POST | /orders | Create an order |
| GET | /orders | List all orders |
| GET | /orders/{id} | Get one order (404 if missing) |
| GET | /metrics | Prometheus metrics |

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the Swagger UI.

## Run tests

```bash
pytest -v
```

## Run with Docker

```bash
docker build -t order-service:1.0 .
docker run -d -p 8000:8000 --name orders order-service:1.0
curl http://localhost:8000/health
```

## Deploy to Kubernetes (kind)

```bash
kind create cluster --name orders
kind load docker-image order-service:1.0 --name orders
kubectl apply -f k8s/
kubectl get pods
kubectl port-forward service/order-service 8080:80
```

The Deployment runs 2 replicas with readiness and liveness probes on /health and CPU/memory limits.

## Monitoring with Prometheus

```bash
docker run -d -p 9090:9090 --name prometheus \
  -v "$(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml" \
  prom/prometheus
```

Useful queries: `orders_created_total`, `rate(http_requests_total[1m])`, `up{job="order-service"}`

## CI/CD

Every push to main runs GitHub Actions: install dependencies, run the pytest suite, and build the Docker image.

## Author

Triveni Battula
