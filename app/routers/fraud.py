"""
app/routers/fraud.py
─────────────────────
POST /v1/fraud/predict — Fraud detection endpoint.
"""
import time
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.fraud import FraudRequest, FraudResponse
from app.db.session import get_db
from app.db.models import FraudPrediction
from app.models.loader import get_model_loader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/fraud", tags=["Fraud Detection"])


@router.post(
    "/predict",
    response_model=FraudResponse,
    summary="Predict transaction fraud probability",
    description=(
        "Accepts transaction features and returns the probability that "
        "the transaction is fraudulent, along with model version and latency."
    ),
)
def predict_fraud(
    payload: FraudRequest,
    db: Session = Depends(get_db),
) -> FraudResponse:
    loader = get_model_loader()

    t0 = time.perf_counter()
    fraud_probability, model_version = loader.predict_fraud(
        transaction_amount=payload.transaction_amount,
        merchant_type=payload.merchant_type,
        country=payload.country,
        time_delta=payload.time_delta,
        device_type=payload.device_type,
    )
    latency_ms = (time.perf_counter() - t0) * 1000

    # ── Persist to DB ─────────────────────────────────────────
    record = FraudPrediction(
        transaction_amount=payload.transaction_amount,
        merchant_type=payload.merchant_type,
        country=payload.country,
        time_delta=payload.time_delta,
        device_type=payload.device_type,
        fraud_probability=fraud_probability,
        model_version=model_version,
        latency_ms=latency_ms,
    )
    db.add(record)
    db.commit()

    logger.info(
        f"[fraud] prob={fraud_probability:.4f} version={model_version} "
        f"latency={latency_ms:.2f}ms"
    )
    return FraudResponse(
        fraud_probability=round(fraud_probability, 4),
        model_version=model_version,
        latency_ms=round(latency_ms, 3),
    )
