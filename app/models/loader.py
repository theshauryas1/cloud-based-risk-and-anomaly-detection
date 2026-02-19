"""
app/models/loader.py
─────────────────────
Singleton ModelLoader: loads both fraud and anomaly models at startup.
Thread-safe via module-level singleton pattern.
"""
import logging
import numpy as np
import joblib
from app.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    """Loads and wraps the fraud + anomaly model pipelines."""

    def __init__(self):
        logger.info("Loading ML models from disk …")
        fraud_artifact   = joblib.load(settings.FRAUD_MODEL_PATH)
        anomaly_artifact = joblib.load(settings.ANOMALY_MODEL_PATH)

        self._fraud_pipeline   = fraud_artifact["pipeline"]
        self._fraud_meta       = fraud_artifact["metadata"]
        self._anomaly_pipeline = anomaly_artifact["pipeline"]
        self._anomaly_meta     = anomaly_artifact["metadata"]

        logger.info(
            f"Models loaded — fraud={self._fraud_meta['model_version']}  "
            f"anomaly={self._anomaly_meta['model_version']}"
        )

    # ── Fraud ──────────────────────────────────────────────────

    def predict_fraud(
        self,
        transaction_amount: float,
        merchant_type: str,
        country: str,
        time_delta: float,
        device_type: str,
    ) -> tuple[float, str]:
        """Returns (fraud_probability, model_version)."""
        enc = self._fraud_meta["encodings"]
        merchant_idx = enc["merchant_type"].get(merchant_type, 0)
        country_idx  = enc["country"].get(country, 0)
        device_idx   = enc["device_type"].get(device_type, 0)

        X = np.array([[transaction_amount, merchant_idx, country_idx,
                       time_delta, device_idx]], dtype=float)
        prob = float(self._fraud_pipeline.predict_proba(X)[0][1])
        return prob, self._fraud_meta["model_version"]

    # ── Anomaly ────────────────────────────────────────────────

    def predict_anomaly(
        self,
        response_time: float,
        error_rate: float,
        cpu_usage: float,
        memory_usage: float,
    ) -> tuple[float, str]:
        """Returns (anomaly_score [0-1], model_version)."""
        X = np.array([[response_time, error_rate, cpu_usage, memory_usage]], dtype=float)

        iso    = self._anomaly_pipeline.named_steps["iso"]
        scaler = self._anomaly_pipeline.named_steps["scaler"]
        X_sc   = scaler.transform(X)
        raw    = float(iso.decision_function(X_sc)[0])

        # Normalise using training-time range stored in metadata
        s_min = self._anomaly_meta["score_range"]["min"]
        s_max = self._anomaly_meta["score_range"]["max"]
        score = 1.0 - (raw - s_min) / (s_max - s_min + 1e-9)
        score = float(np.clip(score, 0.0, 1.0))

        return score, self._anomaly_meta["model_version"]


# ── Module-level singleton ─────────────────────────────────────
_model_loader: ModelLoader | None = None


def get_model_loader() -> ModelLoader:
    """Returns the singleton ModelLoader, initialising it on first call."""
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader()
    return _model_loader
