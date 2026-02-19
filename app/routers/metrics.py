"""
app/routers/metrics.py
───────────────────────
GET /v1/metrics — Aggregated platform metrics endpoint.
Returns total prediction counts, average latencies, and per-model call counts.
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import FraudPrediction, AnomalyPrediction

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["Metrics"])


class MetricsResponse(BaseModel):
    total_predictions: int
    fraud_predictions: int
    anomaly_predictions: int
    avg_fraud_latency_ms: float
    avg_anomaly_latency_ms: float
    avg_fraud_probability: float
    avg_anomaly_score: float


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Platform-level prediction metrics",
    description=(
        "Returns aggregated statistics across both prediction models: "
        "total call counts, average latencies, and average output scores."
    ),
)
def get_metrics(db: Session = Depends(get_db)) -> MetricsResponse:
    # ── Fraud aggregates ──────────────────────────────────────
    fraud_row = db.query(
        func.count(FraudPrediction.id).label("count"),
        func.avg(FraudPrediction.latency_ms).label("avg_latency"),
        func.avg(FraudPrediction.fraud_probability).label("avg_score"),
    ).one()

    # ── Anomaly aggregates ────────────────────────────────────
    anomaly_row = db.query(
        func.count(AnomalyPrediction.id).label("count"),
        func.avg(AnomalyPrediction.latency_ms).label("avg_latency"),
        func.avg(AnomalyPrediction.anomaly_score).label("avg_score"),
    ).one()

    fraud_count      = int(fraud_row.count   or 0)
    anomaly_count    = int(anomaly_row.count or 0)
    total            = fraud_count + anomaly_count

    return MetricsResponse(
        total_predictions=total,
        fraud_predictions=fraud_count,
        anomaly_predictions=anomaly_count,
        avg_fraud_latency_ms=round(float(fraud_row.avg_latency   or 0.0), 3),
        avg_anomaly_latency_ms=round(float(anomaly_row.avg_latency or 0.0), 3),
        avg_fraud_probability=round(float(fraud_row.avg_score    or 0.0), 4),
        avg_anomaly_score=round(float(anomaly_row.avg_score      or 0.0), 4),
    )
