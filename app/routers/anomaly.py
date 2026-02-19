"""
app/routers/anomaly.py
───────────────────────
POST /v1/anomaly/predict — System anomaly detection endpoint.
"""
import time
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.anomaly import AnomalyRequest, AnomalyResponse
from app.db.session import get_db
from app.db.models import AnomalyPrediction
from app.models.loader import get_model_loader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/anomaly", tags=["Anomaly Detection"])


@router.post(
    "/predict",
    response_model=AnomalyResponse,
    summary="Predict system anomaly score",
    description=(
        "Accepts SaaS system metrics (response time, error rate, CPU, memory) "
        "and returns a normalised anomaly score in [0, 1]. "
        "Scores closer to 1 indicate higher anomaly likelihood."
    ),
)
def predict_anomaly(
    payload: AnomalyRequest,
    db: Session = Depends(get_db),
) -> AnomalyResponse:
    loader = get_model_loader()

    t0 = time.perf_counter()
    anomaly_score, model_version = loader.predict_anomaly(
        response_time=payload.response_time,
        error_rate=payload.error_rate,
        cpu_usage=payload.cpu_usage,
        memory_usage=payload.memory_usage,
    )
    latency_ms = (time.perf_counter() - t0) * 1000

    # ── Persist to DB ─────────────────────────────────────────
    record = AnomalyPrediction(
        response_time=payload.response_time,
        error_rate=payload.error_rate,
        cpu_usage=payload.cpu_usage,
        memory_usage=payload.memory_usage,
        anomaly_score=anomaly_score,
        model_version=model_version,
        latency_ms=latency_ms,
    )
    db.add(record)
    db.commit()

    logger.info(
        f"[anomaly] score={anomaly_score:.4f} version={model_version} "
        f"latency={latency_ms:.2f}ms"
    )
    return AnomalyResponse(
        anomaly_score=round(anomaly_score, 4),
        model_version=model_version,
        latency_ms=round(latency_ms, 3),
    )
