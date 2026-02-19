"""
app/main.py
────────────
FastAPI application entry-point.

Startup sequence:
  1. DB tables are created (create_all).
  2. ML models are loaded into the singleton ModelLoader.
  3. Routers are mounted.

Middleware:
  - Latency header (X-Process-Time-ms) on every response.
  - Structured request logging.
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.init_db import init_db
from app.models.loader import get_model_loader
from app.routers import fraud, anomaly, metrics
from app.config import settings

# ── Logging setup ─────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Risk & Anomaly Detection Platform starting up ===")
    logger.info(f"Environment : {settings.ENV}")
    logger.info(f"Database    : {settings.DATABASE_URL.split('@')[-1]}")  # hide credentials
    init_db()
    logger.info("Database tables initialised.")
    get_model_loader()   # warm up the singleton
    logger.info("ML models loaded and ready.")
    yield
    logger.info("=== Platform shutting down ===")


# ── Application ───────────────────────────────────────────────
app = FastAPI(
    title="Risk & Anomaly Detection Platform",
    description=(
        "Cloud-native ML platform exposing two business-domain inference APIs:\n\n"
        "- **Fraud Detection** — LogisticRegression on transaction features\n"
        "- **Anomaly Detection** — IsolationForest on SaaS system metrics\n\n"
        "All predictions are persisted to the database with latency tracking."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Latency middleware ────────────────────────────────────────
@app.middleware("http")
async def add_latency_header(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.3f}"
    logger.debug(f"{request.method} {request.url.path} → {response.status_code} "
                 f"({elapsed_ms:.2f}ms)")
    return response


# ── Routers ───────────────────────────────────────────────────
app.include_router(fraud.router)
app.include_router(anomaly.router)
app.include_router(metrics.router)


# ── Health check ──────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Service health check")
def health():
    return {
        "status": "ok",
        "environment": settings.ENV,
        "fraud_model": get_model_loader()._fraud_meta["model_version"],
        "anomaly_model": get_model_loader()._anomaly_meta["model_version"],
    }
