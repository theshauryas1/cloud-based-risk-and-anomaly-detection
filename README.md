# 🛡️ Risk & Anomaly Detection Platform

> **Cloud-native ML platform** exposing two production-grade inference APIs:  
> **Fraud Detection** (fintech) · **Anomaly Detection** (SaaS infrastructure)  
> Built with FastAPI · scikit-learn · PostgreSQL · Docker · GitHub Actions

[![CI](https://github.com/theshauryas1/cloud-based-risk-and-anomaly-detection/actions/workflows/ci.yml/badge.svg)](https://github.com/theshauryas1/cloud-based-risk-and-anomaly-detection/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)
[![Render](https://img.shields.io/badge/deployed-Render-46E3B7.svg)](https://cloud-based-risk-and-anomaly-detection.onrender.com/health)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🌐 **Live API:** https://cloud-based-risk-and-anomaly-detection.onrender.com  
📖 **Swagger Docs:** https://cloud-based-risk-and-anomaly-detection.onrender.com/docs


---

## 📐 Architecture

```
Client (JSON)
     │
     ▼
 FastAPI App  ──── Middleware (latency header, CORS, logging)
     │
     ├── POST /v1/fraud/predict   → LogisticRegression
     ├── POST /v1/anomaly/predict → IsolationForest
     ├── GET  /v1/metrics         → DB aggregation query
     └── GET  /health             → model version status
     │
     ▼
 SQLAlchemy ORM
     │
     ├── SQLite  (local dev / tests)
     └── PostgreSQL  (Docker · Neon · production)
```

---

## 🔌 API Endpoints

### `POST /v1/fraud/predict`
Detects fraudulent bank transactions using a Logistic Regression classifier.

**Request**
```json
{
  "transaction_amount": 2500.00,
  "merchant_type": "electronics",
  "country": "US",
  "time_delta": 5.2,
  "device_type": "mobile"
}
```

**Response**
```json
{
  "fraud_probability": 0.7431,
  "model_version": "fraud-v1.0.0",
  "latency_ms": 1.243
}
```

---

### `POST /v1/anomaly/predict`
Detects infrastructure anomalies in SaaS systems using Isolation Forest.

**Request**
```json
{
  "response_time": 950.0,
  "error_rate": 0.12,
  "cpu_usage": 91.0,
  "memory_usage": 87.0
}
```

**Response**
```json
{
  "anomaly_score": 0.8912,
  "model_version": "anomaly-v1.0.0",
  "latency_ms": 0.887
}
```

`anomaly_score` is normalised to **[0, 1]** — higher score = more anomalous.

---

### `GET /v1/metrics`
Returns platform-level aggregated statistics from the database.

**Response**
```json
{
  "total_predictions": 142,
  "fraud_predictions": 89,
  "anomaly_predictions": 53,
  "avg_fraud_latency_ms": 1.154,
  "avg_anomaly_latency_ms": 0.923,
  "avg_fraud_probability": 0.3812,
  "avg_anomaly_score": 0.4201
}
```

---

### `GET /health`
Returns service health and loaded model versions.

```json
{
  "status": "ok",
  "environment": "development",
  "fraud_model": "fraud-v1.0.0",
  "anomaly_model": "anomaly-v1.0.0"
}
```

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI 0.110 + Uvicorn |
| ML — Fraud | scikit-learn `LogisticRegression` |
| ML — Anomaly | scikit-learn `IsolationForest` |
| ORM | SQLAlchemy 2.0 |
| DB (local) | SQLite (auto-configured) |
| DB (docker) | PostgreSQL 15 |
| DB (cloud) | Neon Postgres (free tier) |
| Containerisation | Docker · docker-compose |
| CI/CD | GitHub Actions |
| Deployment | Render (free tier) |
| Testing | pytest + httpx |

---

## 📂 Project Structure

```
risk-anomaly-platform/
├── app/
│   ├── main.py              # FastAPI app, lifespan, middleware
│   ├── config.py            # Pydantic settings (env vars)
│   ├── db/
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── session.py       # Engine + SessionLocal + get_db
│   │   └── init_db.py       # Table creation on startup
│   ├── models/
│   │   ├── train_fraud.py   # LogisticRegression trainer
│   │   ├── train_anomaly.py # IsolationForest trainer
│   │   ├── loader.py        # Singleton ModelLoader
│   │   └── artifacts/       # .pkl files (auto-generated)
│   ├── routers/
│   │   ├── fraud.py         # POST /v1/fraud/predict
│   │   ├── anomaly.py       # POST /v1/anomaly/predict
│   │   └── metrics.py       # GET  /v1/metrics
│   └── schemas/
│       ├── fraud.py         # Request/Response Pydantic models
│       └── anomaly.py
├── tests/
│   ├── conftest.py          # In-memory SQLite fixtures
│   ├── test_fraud.py
│   ├── test_anomaly.py
│   ├── test_metrics.py
│   └── test_health.py
├── .github/workflows/
│   ├── ci.yml               # Lint → Test → Docker Build
│   └── deploy.yml           # Render deploy hook on main push
├── Dockerfile               # Multi-stage production image
├── docker-compose.yml       # App + Postgres services
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start (Local Dev)

### Prerequisites
- Python 3.11+
- pip

### 1 — Clone and install
```powershell
git clone https://github.com/theshauryas1/cloud-based-risk-and-anomaly-detection.git
cd cloud-based-risk-and-anomaly-detection

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
```

### 2 — Train ML models (one-time)
```powershell
python -m app.models.train_fraud
python -m app.models.train_anomaly
```

### 3 — Configure environment
```powershell
copy .env.example .env
# Leave DATABASE_URL blank → auto-uses SQLite locally
```

### 4 — Start the server
```powershell
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## 🧪 Running Tests

```powershell
pytest tests/ -v
```

Tests use an **in-memory SQLite database** — no external services required.  
22 tests cover schema validation, field constraints, 422 error handling, and semantic model behaviour.

---

## 🐳 Docker

### With docker-compose (app + Postgres)
```powershell
docker-compose up --build
```
The app will be available at **http://localhost:8000**.  
PostgreSQL data is persisted in the `postgres_data` named volume.

### Build image only
```powershell
docker build -t risk-anomaly-platform .
docker run -p 10000:10000 -e ENV=development risk-anomaly-platform
```

---

## ☁️ Cloud Deployment (Render + Neon)

### Step 1 — Create Neon Postgres (Free)

1. Go to [neon.tech](https://neon.tech) → Create a free account
2. Create a new **Project** (choose nearest region)
3. Copy the **Connection String** — it looks like:
   ```
   postgresql://user:password@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2 — Push to GitHub

```powershell
git init
git add .
git commit -m "feat: initial production-ready platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/risk-anomaly-platform.git
git push -u origin main
```

### Step 3 — Deploy to Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Environment**: `Docker`
   - **Branch**: `main`
   - **Region**: nearest to you
4. Add **Environment Variables**:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require` |
   | `ENV` | `production` |
   | `LOG_LEVEL` | `INFO` |

5. Click **Deploy** — Render builds the Docker image, trains models, starts the container

> **Port note:** Render automatically sets `$PORT`. The Dockerfile uses `${PORT:-10000}` so it works without any manual config.

### Step 4 — Wire up Auto-deploy (CI/CD)

1. On Render: **Settings** → **Deploy Hook** → copy the URL
2. On GitHub: **Settings** → **Secrets** → New secret: `RENDER_DEPLOY_HOOK_URL` = paste URL
3. Now every push to `main` auto-deploys via GitHub Actions

### Step 5 — Verify Live Deployment

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Fraud prediction
curl -X POST https://your-app-name.onrender.com/v1/fraud/predict \
  -H "Content-Type: application/json" \
  -d "{\"transaction_amount\":2500,\"merchant_type\":\"electronics\",\"country\":\"US\",\"time_delta\":5.2,\"device_type\":\"mobile\"}"

# Anomaly detection
curl -X POST https://your-app-name.onrender.com/v1/anomaly/predict \
  -H "Content-Type: application/json" \
  -d "{\"response_time\":950,\"error_rate\":0.12,\"cpu_usage\":91,\"memory_usage\":87}"

# Platform metrics
curl https://your-app-name.onrender.com/v1/metrics

# Swagger UI
open https://your-app-name.onrender.com/docs
```

### Common Render Build Errors

| Error | Fix |
|---|---|
| `psycopg2` not found | Ensure `psycopg2-binary` is in `requirements.txt` |
| `DATABASE_URL` not set | Add it in Render → Environment tab |
| Port mismatch | Dockerfile uses `${PORT:-10000}` — no change needed |
| Model not found | Docker bakes models at build time — re-trigger deploy |

---

## 🔄 CI/CD Pipeline

```
Push / PR
    │
    ▼
  flake8 lint
    │
    ▼
  pytest  (in-memory SQLite, no external deps)
    │
    ▼
  docker build  (validates image, not pushed on PR)
    │         (only on main push)
    ▼
  Render deploy hook  →  live update
```

---

## 🗄️ Database Notes

> **For simplicity, table auto-creation (`create_all()`) is used on startup.**  
> Production systems would use managed migrations via [Alembic](https://alembic.sqlalchemy.org/).  
> To add Alembic migrations: `alembic init alembic && alembic revision --autogenerate -m "initial"`

---

## 📊 Model Details

| Model | Algorithm | Training Data | Features |
|---|---|---|---|
| Fraud | `LogisticRegression` (C=1.0) | 2000 synthetic transactions | amount, merchant, country, time_delta, device |
| Anomaly | `IsolationForest` (contamination=5%) | 1800 normal + 200 anomalous metrics | response_time, error_rate, cpu, memory |

Both models are trained once and committed as `.pkl` artifacts, loaded instantly at startup via a singleton `ModelLoader`.  
Each prediction row in the DB stores the `model_version` string for full auditability.

---

## 📄 License

MIT © 2026
